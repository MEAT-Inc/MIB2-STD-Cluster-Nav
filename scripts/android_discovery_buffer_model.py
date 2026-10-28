"""Synthetic host buffer/allocator model. NOT a native ABI shim or vehicle hook."""
from dataclasses import dataclass
import unittest
from android_discovery_wire_fixture import uint,message,add_cluster_descriptor

class Heap:
    def __init__(self): self.blocks={};self.frees=[];self.next=1;self.fail_alloc=False;self.fail_store=False
    def alloc(self,n):
        if self.fail_alloc:raise MemoryError('injected allocation failure')
        key=self.next;self.next+=1;self.blocks[key]=bytearray(n);return key
    def store(self,key,data):
        if self.fail_store:raise OSError('injected copy failure')
        if len(data)!=len(self.blocks[key]):raise ValueError('size mismatch')
        self.blocks[key][:]=data
    def free(self,key):
        if key not in self.blocks:raise ValueError('double or invalid free')
        del self.blocks[key];self.frees.append(key)
@dataclass
class Buffer:
    pointer:int
    capacity:int
    start:int
    end:int

def rewrite_model(buf,heap,transform,native_result=True,max_bytes=1024*1024):
    """Preserve native return; retain original buffer on all pre-publication failures."""
    temporary=None
    if not native_result:return native_result
    try:
        data=heap.blocks[buf.pointer]
        if not (buf.start==0 and 2<=buf.end<=buf.capacity<=len(data) and buf.end<=max_bytes):return native_result
        original=bytes(data[:buf.end])
        if original[:2]!=b'\x00\x06':return native_result
        payload=transform(original[2:])
        if not isinstance(payload,bytes):return native_result
        packet=original[:2]+payload
        if len(packet)>max_bytes or len(packet)>0x7fffffff:return native_result
        temporary=heap.alloc(len(packet));heap.store(temporary,packet)
    except (KeyError,ValueError,MemoryError,OSError):
        if temporary is not None:heap.free(temporary)
        return native_result
    old=buf.pointer
    buf.pointer,buf.capacity,buf.start,buf.end=temporary,len(packet),0,len(packet)
    heap.free(old)
    return native_result

class BufferTests(unittest.TestCase):
    def setUp(self):
        self.heap=Heap();cfg=uint(1,1)+uint(2,2)
        self.payload=message(1,uint(1,2)+message(3,uint(1,3)+message(4,cfg)))
        self.packet=b'\x00\x06'+self.payload
        key=self.heap.alloc(len(self.packet));self.heap.store(key,self.packet)
        self.buf=Buffer(key,len(self.packet),0,len(self.packet));self.original=Buffer(**vars(self.buf))
        self.transform=lambda p:add_cluster_descriptor(p,2,64)
    def unchanged(self):
        self.assertEqual(self.buf,self.original);self.assertEqual(bytes(self.heap.blocks[self.buf.pointer]),self.packet)
        self.assertNotIn(self.original.pointer,self.heap.frees)
    def test_success_preserves_prefix_and_main(self):
        self.assertIs(rewrite_model(self.buf,self.heap,self.transform),True)
        data=bytes(self.heap.blocks[self.buf.pointer]);self.assertTrue(data.startswith(self.packet))
        self.assertEqual(self.heap.frees,[self.original.pointer]);self.assertEqual(self.buf.end,self.buf.capacity)
        self.assertEqual(self.buf.start,0)
    def test_allocation_failure_keeps_original(self):
        self.heap.fail_alloc=True;rewrite_model(self.buf,self.heap,self.transform);self.unchanged()
    def test_copy_failure_frees_temporary_only(self):
        self.heap.fail_store=True;rewrite_model(self.buf,self.heap,self.transform);self.unchanged()
        self.assertEqual(self.heap.frees,[2]);self.assertEqual(list(self.heap.blocks),[1])
    def test_parse_failure_keeps_original(self):
        def fail(_):raise ValueError('malformed protobuf')
        rewrite_model(self.buf,self.heap,fail);self.unchanged()
    def test_native_failure_preserved_without_transform(self):
        def fail(_):raise AssertionError('transform must not run')
        self.assertIs(rewrite_model(self.buf,self.heap,fail,False),False);self.unchanged()
    def test_other_message_id_untouched(self):
        self.heap.blocks[self.buf.pointer][1]=8
        before=bytes(self.heap.blocks[self.buf.pointer]);rewrite_model(self.buf,self.heap,self.transform)
        self.assertEqual(self.buf,self.original);self.assertEqual(bytes(self.heap.blocks[self.buf.pointer]),before)
        self.assertEqual(self.heap.frees,[])
    def test_invalid_bounds_rejected(self):
        for cap,start,end in [(1,0,2),(self.buf.capacity,1,self.buf.end),(self.buf.capacity,0,self.buf.capacity+1),(self.buf.capacity+1,0,self.buf.end)]:
            with self.subTest(cap=cap,start=start,end=end):
                candidate=Buffer(self.original.pointer,cap,start,end);before=Buffer(**vars(candidate))
                rewrite_model(candidate,self.heap,self.transform);self.assertEqual(candidate,before);self.assertEqual(self.heap.frees,[])
    def test_max_boundary_accepted(self):
        target=self.packet+b'x';rewrite_model(self.buf,self.heap,lambda p:p+b'x',max_bytes=len(target))
        self.assertEqual(bytes(self.heap.blocks[self.buf.pointer]),target)
    def test_over_limit_keeps_original(self):
        rewrite_model(self.buf,self.heap,self.transform,max_bytes=len(self.packet));self.unchanged()
    def test_queue_copy_survives_caller_free(self):
        rewrite_model(self.buf,self.heap,self.transform)
        queued=bytes(self.heap.blocks[self.buf.pointer][self.buf.start:self.buf.end])
        self.heap.free(self.buf.pointer)
        self.assertTrue(queued.startswith(self.packet));self.assertEqual(len(self.heap.frees),2)
        self.assertEqual(self.heap.blocks,{})
    def test_single_free_contract(self):
        rewrite_model(self.buf,self.heap,self.transform);self.heap.free(self.buf.pointer)
        with self.assertRaises(ValueError):self.heap.free(self.buf.pointer)

if __name__=='__main__':unittest.main()

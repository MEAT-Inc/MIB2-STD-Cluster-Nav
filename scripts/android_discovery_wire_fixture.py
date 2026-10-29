"""Host-only protobuf fixture, not a vehicle hook or complete discovery implementation.

Preserves the input response bytes and appends a cloned video descriptor with
new service ID and modern media-sink display metadata. A real receiver must
ALSO register a working endpoint/input service and implement its lifecycle.
"""
from dataclasses import dataclass
from pathlib import Path
import json, unittest

@dataclass(frozen=True)
class Field:
    number: int
    wire: int
    value: object
    raw: bytes

def varint(value):
    if not 0 <= value < 1 << 64: raise ValueError('uint64 required')
    out=bytearray()
    while value>127: out.append((value&127)|128);value >>=7
    out.append(value);return bytes(out)

def readvar(data,pos):
    value=0
    for i in range(10):
        if pos>=len(data): raise ValueError('truncated varint')
        c=data[pos];pos+=1
        if i==9 and c>1: raise ValueError('overflow')
        value|=(c&127)<<(i*7)
        if c<128:return value,pos
    raise ValueError('overlong varint')

def fields(data):
    out=[];pos=0
    while pos<len(data):
        start=pos;tag,pos=readvar(data,pos);number,wire=tag>>3,tag&7
        if not 1<=number<1<<29: raise ValueError('invalid field number')
        if wire==0:value,pos=readvar(data,pos)
        elif wire in (1,5):
            n=8 if wire==1 else 4
            if pos+n>len(data):raise ValueError('truncated fixed field')
            value=data[pos:pos+n];pos+=n
        elif wire==2:
            n,pos=readvar(data,pos)
            if n>len(data)-pos:raise ValueError('truncated bytes field')
            value=data[pos:pos+n];pos+=n
        else:raise ValueError('groups/reserved wire types are not supported')
        out.append(Field(number,wire,value,data[start:pos]))
    return out

def uint(number,value):return varint(number<<3)+varint(value)
def message(number,value):return varint((number<<3)|2)+varint(len(value))+value

def single(items,number,wire):
    match=[x for x in items if x.number==number]
    if len(match)!=1 or match[0].wire!=wire:raise ValueError(f'exactly one field {number} wire {wire} required')
    return match[0]

def add_cluster_descriptor(response,template_id,new_id,display_id=1):
    if not 1<=new_id<=254 or not 1<=display_id<=255:raise ValueError('invalid illustrative ID')
    services=[]
    for f in fields(response):
        if f.number==1:
            if f.wire!=2:raise ValueError('Service must be a message')
            body=fields(f.value);sid=single(body,1,0).value
            services.append((sid,body))
    if new_id in [s for s,b in services]:raise ValueError('service ID already occupied')
    matches=[b for s,b in services if s==template_id]
    if len(matches)!=1:raise ValueError('unique template service required')
    body=matches[0];media=single(body,3,2)
    mf=fields(media.value)
    if not any(f.number==4 and f.wire==2 for f in mf):raise ValueError('template has no video configuration')
    # Change only modern metadata fields on the NEW copy, never the old main service.
    media_copy=b''.join(f.raw for f in mf if f.number not in (6,7))+uint(6,display_id)+uint(7,1)
    service_copy=b''.join(uint(1,new_id) if f.number==1 else message(3,media_copy) if f.number==3 else f.raw for f in body)
    return response+message(1,service_copy)

def add_cluster_services(response,template_id,video_id,input_id,display_id=1):
    """OFFBOARD ONLY: video plus minimal paired input; creates no live endpoint.

    Input field 5 is display id. The minimal key list follows the working DHU
    pair described in the upstream video_sink_hook.c reference. Never deploy
    this descriptor until both actual protocol endpoints exist.
    """
    if video_id==input_id or not 1<=input_id<=254:raise ValueError('distinct valid service IDs required')
    seen=set()
    for f in fields(response):
        if f.number!=1:continue
        if f.wire!=2:raise ValueError('Service must be a message')
        sid=single(fields(f.value),1,0).value
        if sid in seen:raise ValueError('duplicate original service ID')
        seen.add(sid)
        if sid==input_id:raise ValueError('input service ID already occupied')
    candidate=add_cluster_descriptor(response,template_id,video_id,display_id)
    # Packed keycodes: DPAD_CENTER (23) and 65536, no fabricated touchscreen.
    input_media=message(1,varint(23)+varint(65536))+uint(5,display_id)
    input_service=uint(1,input_id)+message(4,input_media)
    return candidate+message(1,input_service)

# Independent fixture decoder: deliberately uses separate byte-walking logic.
def independent_decode(data):
    pos=0;out=[]
    def take_var():
        nonlocal pos
        value=shift=0
        while True:
            c=data[pos];pos+=1;value|=(c&127)<<shift
            if c<128:return value
            shift+=7
            if shift>63:raise ValueError('bad varint')
    while pos<len(data):
        tag=take_var();n,w=tag>>3,tag&7
        if w==0:v=take_var()
        elif w==2:
            length=take_var();v=data[pos:pos+length];pos+=length
        elif w in (1,5):
            length=8 if w==1 else 4;v=data[pos:pos+length];pos+=length
        else:raise ValueError('unsupported fixture field')
        if pos>len(data):raise ValueError('truncated')
        out.append((n,w,v))
    return out

class WireTests(unittest.TestCase):
    def setUp(self):
        self.config=uint(1,1)+uint(2,2)+uint(5,138)
        self.media=uint(1,3)+message(4,self.config)+message(101,b'unknown-media')
        self.service=uint(1,2)+message(3,self.media)+uint(104,77)
        self.response=message(1,self.service)+message(103,b'unknown-response')
    def test_preserves_main_and_extensions(self):
        result=add_cluster_descriptor(self.response,2,64)
        self.assertTrue(result.startswith(self.response))
        tree=independent_decode(result);services=[v for n,w,v in tree if n==1]
        self.assertEqual(services[0],self.service)
        second=independent_decode(services[1]);self.assertIn((1,0,64),second);self.assertIn((104,0,77),second)
        media=independent_decode(next(v for n,w,v in second if n==3))
        self.assertIn((6,0,1),media);self.assertIn((7,0,1),media)
        self.assertIn((101,2,b'unknown-media'),media)
        self.assertIn((4,2,self.config),media)
    def test_rejects_collision(self):
        with self.assertRaises(ValueError):add_cluster_descriptor(self.response,2,2)
    def test_rejects_ambiguous_template(self):
        with self.assertRaises(ValueError):add_cluster_descriptor(self.response+message(1,self.service),2,64)
    def test_existing_metadata_replaced_only_on_clone(self):
        media=self.media+uint(6,0)+uint(7,0)
        original=message(1,uint(1,2)+message(3,media))
        result=add_cluster_descriptor(original,2,64)
        self.assertTrue(result.startswith(original))
        clone=independent_decode(independent_decode(result)[1][2])
        decoded=independent_decode(next(v for n,w,v in clone if n==3))
        self.assertEqual([v for n,w,v in decoded if n==7],[1])
    def test_malformed_rejected(self):
        for data in (b'\x0a\x08x',b'\x00',b'\x0b',b'\x08'+b'\xff'*10):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):fields(data)
    def test_fixed_unknown_preserved(self):
        extension=varint((99<<3)|5)+b'abcd'
        result=add_cluster_descriptor(self.response+extension,2,64)
        self.assertTrue(result.startswith(self.response+extension))

if __name__=='__main__':
    unittest.main()

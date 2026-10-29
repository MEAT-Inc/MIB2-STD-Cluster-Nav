import contextlib,io,json,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import collect_trace_tcp as m
class FakeSocket:
 def __init__(self,parts):self.parts=list(parts);self.requests=[]
 def settimeout(self,value):self.timeout=value
 def recv(self,n):
  self.requests.append(n);part=self.parts.pop(0)
  if isinstance(part,Exception):raise part
  if len(part)>n:self.parts.insert(0,part[n:]);part=part[:n]
  return part
class TcpTests(unittest.TestCase):
 def test_plan_offline(self):
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory') as inv,patch.object(m.socket,'create_connection') as conn,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main([]),0);inv.assert_not_called();conn.assert_not_called();self.assertFalse((Path(t)/'delphi-dump').exists())
 def test_exact_byte_cap(self):
  out=io.BytesIO();s=FakeSocket([b'abcdef'])
  with patch.object(m.time,'monotonic',return_value=0):r=m.receive(s,out,30,4)
  self.assertEqual(out.getvalue(),b'abcd');self.assertEqual(r['stop_reason'],'byte_limit');self.assertEqual(s.requests,[4])
 def test_eof_and_binary_preservation(self):
  out=io.BytesIO();s=FakeSocket([b'a\0\xff\n',b''])
  with patch.object(m.time,'monotonic',return_value=0):r=m.receive(s,out,30,100)
  self.assertEqual(out.getvalue(),b'a\0\xff\n');self.assertEqual(r['stop_reason'],'peer_closed')
 def test_timeout_obeys_deadline(self):
  out=io.BytesIO();s=FakeSocket([socket.timeout()])
  with patch.object(m.time,'monotonic',side_effect=[0,0,31,31]):r=m.receive(s,out,30,100)
  self.assertEqual(r['bytes'],0);self.assertEqual(r['stop_reason'],'duration')
 def test_existing_client_detection(self):
  self.assertTrue(m.port_state(b'12 I4TCP *.15361 *.* LISTEN','LISTEN'))
  self.assertTrue(m.port_state(b'12 I4TCP 192.168.1.4.15361 192.168.1.10.1234 ESTABLISHED','ESTABLISHED'))
  self.assertFalse(m.port_state(b'153610 LISTEN','LISTEN'))
 def test_refuse_existing_client_before_tcp(self):
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory',return_value=([],{'trace-fds':b'*.15361 x.1234 ESTABLISHED'})),patch.object(m.socket,'create_connection') as conn,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main(['--run']),2);conn.assert_not_called()
   r=json.loads(next(Path(t).glob('delphi-dump/*/trace-tcp-summary.json')).read_text());self.assertFalse(r['capture_complete'])
 def test_collection_preserves_raw_and_never_sends(self):
  class Socket(FakeSocket):
   def __enter__(self):return self
   def __exit__(self,*args):pass
  def inventory(a,folder,commands):
   (folder/'trace-fds.txt').write_bytes(b'*.15361 *.* LISTEN')
   return [],{'trace-fds':b'*.15361 *.* LISTEN'}
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory',side_effect=inventory),patch.object(m.socket,'create_connection',return_value=Socket([b'raw\x00trace',b''])),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main(['--run']),2)
   folder=next(Path(t).glob('delphi-dump/*'));r=json.loads((folder/'trace-tcp-summary.json').read_text())
   self.assertEqual((folder/'trace.bin').read_bytes(),b'raw\x00trace');self.assertEqual(r['application_bytes_sent'],0);self.assertTrue(r['trace_received']);self.assertFalse(r['capture_complete']);self.assertFalse(r['display_recovery_verified'])
 def test_invalid_limits(self):
  for args in (['--seconds','0'],['--seconds','121'],['--max-bytes','0']):
   with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main(args)
if __name__=='__main__':unittest.main()

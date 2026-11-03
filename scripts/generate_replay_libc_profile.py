"""Extract relocation-free libc entry fingerprints from a supplied ARM ELF."""
import argparse,hashlib,json,struct
from pathlib import Path

def generate(source,target):
 b=source.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01';assert struct.unpack_from('<HH',b,16)==(3,40)
 po=struct.unpack_from('<I',b,28)[0];pe,pn=struct.unpack_from('<HH',b,42);segments=[struct.unpack_from('<8I',b,po+i*pe) for i in range(pn)]
 def read(va,n):
  p=next(p for p in segments if p[0]==1 and p[2]<=va and va+n<=p[2]+p[4]);o=p[1]+va-p[2];return b[o:o+n]
 dynamic=next(p for p in segments if p[0]==2);tags={}
 for tag,val in struct.iter_unpack('<II',read(dynamic[2],dynamic[4])):
  if not tag:break
  tags[tag]=val
 count=struct.unpack('<II',read(tags[4],8))[1];syms={}
 for i in range(count):
  name,value,size,info,other,section=struct.unpack('<IIIBBH',read(tags[6]+16*i,16))
  if section and name:
   chars=bytearray();at=tags[5]+name
   while True:
    v=read(at,1);at+=1
    if v==b'\0':break
    chars.extend(v)
   syms[chars.decode()]=value
 offsets=[syms[n] for n in ('open','write','close')];prefix=[read(v,32) for v in offsets];relocs=[]
 for address,size in ((tags.get(17,0),tags.get(18,0)),(tags.get(23,0),tags.get(2,0))):
  if address:
   for dst,info in struct.iter_unpack('<II',read(address,size)):relocs.append(dst)
 if any(v<=dst<v+32 for v in offsets for dst in relocs):raise ValueError('Mutable entry fingerprint')
 text='#ifndef REPLAY_EXPECTED_LIBC_H\n#define REPLAY_EXPECTED_LIBC_H\n#include "libc-profile.h"\nstatic const struct replay_libc_profile replay_expected_libc={{'+','.join(hex(v)+'u' for v in offsets)+'},{'+','.join('{'+','.join(hex(v) for v in p)+'}' for p in prefix)+'}};\n#endif\n'
 target.write_bytes(text.encode());return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),offsets=offsets,code=[p.hex() for p in prefix],relocation_free=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('target',type=Path);p.add_argument('--metadata',type=Path);a=p.parse_args();m=generate(a.source,a.target)
 if a.metadata:a.metadata.write_text(json.dumps(m,indent=2))
 print('Generated libc profile',m['sha256'])

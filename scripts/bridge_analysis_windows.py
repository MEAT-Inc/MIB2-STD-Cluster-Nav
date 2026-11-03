"""Focused offline ARM windows; does not execute firmware or write outputs."""
from project_console import console_session, log as print
with console_session(__file__, __doc__, enabled=__name__ == '__main__'):
    from pathlib import Path
    import io, struct, sys, re
    BASE=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(BASE/'.tools/python'))
    from elftools.elf.elffile import ELFFile
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
    elf=ELFFile(io.BytesIO((BASE/'delphi-dump/extbin/apps/bin/NavigationServer').read_bytes()))
    segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    def read(a,n):
     for start,data in segs:
      if start<=a and a+n<=start+len(data): return data[a-start:a-start+n]
     return b''
    def string(a):
     b=read(a,250).split(b'\0')[0]
     return b.decode('ascii') if b and all(32<=x<127 for x in b) else ''
    md=Cs(CS_ARCH_ARM,CS_MODE_ARM)
    ranges=[(0x1e4688,0x1e4738),(0x1ee640,0x1ee6f8),(0x1fa420,0x1fa4d0)]
    if len(sys.argv)>1:ranges=[tuple(int(x,16) for x in arg.split(':')) for arg in sys.argv[1:]]
    for a,b in ranges:
     print(f'WINDOW {a:#x}:{b:#x}')
     for va,sz,mn,op in md.disasm_lite(read(a,b-a),a):
      note=''
      m=re.search(r'\[pc, #(-?0x[0-9a-f]+|-?\d+)\]',op)
      if m:
       raw=read(va+8+int(m[1],0),4)
       if len(raw)==4:
        v=struct.unpack('<I',raw)[0];note=f' literal={v:#x} {string(v)}'
      print(f'{va:08x} {mn:8} {op}{note}')

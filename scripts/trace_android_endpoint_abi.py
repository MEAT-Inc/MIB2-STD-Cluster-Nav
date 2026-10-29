"""Read-only endpoint/vtable ABI trace of the fingerprinted Delphi binaries."""
import hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
from run_androidauto_observer import REFERENCES
OUT=ROOT/'delphi-analysis/control-runtime'
def inspect(name,relative,expected):
    blob=(ROOT/relative).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=expected:raise ValueError('Wrong acquired image: '+name)
    e=ELFFile(io.BytesIO(blob));dyn=e.get_section_by_name('.dynsym');symbols=list(dyn.iter_symbols());by_name={s.name:s for s in symbols};labels={s['st_value']:s.name for s in symbols if s['st_value']}
    loads=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    def read(address,length):
        for start,data in loads:
            if start<=address and address+length<=start+len(data):return data[address-start:address-start+length]
        raise ValueError('Unmapped file bytes at '+hex(address))
    reloc={}
    for section in e.iter_sections():
        if section['sh_type'] not in ('SHT_REL','SHT_RELA'):continue
        sy=e.get_section(section['sh_link'])
        for r in section.iter_relocations():
            s=sy.get_symbol(r['r_info_sym']);reloc[r['r_offset']]=(r['r_info_type'],s.name,s['st_value'],s['st_shndx'])
    plt=e.get_section_by_name('.plt');rp=e.get_section_by_name('.rel.plt')
    if plt and rp:
        sy=e.get_section(rp['sh_link'])
        for i,r in enumerate(rp.iter_relocations()):labels[plt['sh_addr']+20+i*12]=sy.get_symbol(r['r_info_sym']).name+' [PLT]'
    tables={};lines=[]
    names=('_ZTV9VideoSink','_ZTV13MediaSinkBase','_ZTV20ProtocolEndpointBase','_ZTV11InputSource') if name=='receiver' else ('_ZTV20AaVideoSinkCallbacks','_ZTV19IVideoSinkCallbacks')
    for table in names:
        s=by_name[table];entries=[]
        if s['st_size']%4:raise ValueError('Misaligned vtable')
        for offset in range(8,s['st_size'],4):
            va=s['st_value']+offset;raw=struct.unpack('<I',read(va,4))[0];r=reloc.get(va);value=raw;label=labels.get(raw,'')
            if r:
                kind,symbol,sv,shndx=r
                if kind==2:value=raw+sv;label=symbol
                elif kind==23:value=raw;label=labels.get(raw,'')
                else:raise ValueError('Unhandled vtable relocation '+str(r))
            entries.append(dict(slot=hex(offset-8),address=hex(value),symbol=label,relocation=r[0] if r else None))
        tables[table]=dict(address=hex(s['st_value']),address_point=hex(s['st_value']+8),bytes=s['st_size'],entries=entries)
    ranges=[]
    if name=='receiver':
        for s in symbols:
            if s['st_value'] and s['st_size'] and s['st_info']['type']=='STT_FUNC' and any(k in s.name for k in ('9VideoSink','13MediaSinkBase','20ProtocolEndpointBase','11InputSource')):ranges.append((s.name,s['st_value'],s['st_size']))
    else:
        ranges=[('ProtocolEndpointBase_local_constructor',0x1208fc,0x88),('MediaSinkBase_local_constructor',0x1215d8,0x84),('VideoSink_member_initializers',0x122690,0x78),('VideoSink_local_constructor',0x12165c,0xa0),('VideoSink_allocation_wrapper',0x12174c,0xc0),('app_video_initialize',0x124ccc,0x49c),('AaVideoSinkCallbacks_methods',0x125168,0x988),('AaVideoSinkCallbacks_constructor',0x125ca0,0x1c8),('AaVideoSinkCallbacks_destructors',0x125e68,0x1a0)]
    md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.detail=True;md.skipdata=True
    for method,address,size in sorted(ranges,key=lambda x:x[1]):
        lines.append('\nFUNCTION '+method+' @ '+hex(address)+' size '+hex(size))
        for ins in md.disasm(read(address,size),address):
            note=labels.get(ins.address,'')
            if ins.id and ins.mnemonic in ('b','bl') and ins.operands:note+=' '+labels.get(ins.operands[0].imm,'')
            lines.append(f'{ins.address:08x} {ins.mnemonic:8} {ins.op_str:42} {note}')
    (OUT/('endpoint-abi-'+name+'.assembly.txt')).write_text('\n'.join(lines),encoding='utf-8')
    return dict(sha256=hashlib.sha256(blob).hexdigest(),vtables=tables,functions_traced=len(ranges))
def main():
    OUT.mkdir(exist_ok=True)
    result=dict(receiver=inspect('receiver','delphi-dump/extbin/apps/lib/libautoreceiver.so.1',REFERENCES['receiver.reference'][2]),app=inspect('app','delphi-dump/extbin/apps/bin/AndroidAuto',REFERENCES['AndroidAuto.original'][2]))
    (OUT/'endpoint-abi-vtables.json').write_text(json.dumps(result,indent=2))
    for name,r in result.items():print(name,':',r['functions_traced'],'traces;',len(r['vtables']),'vtables')
if __name__=='__main__':main()

"""Targeted, annotated offline disassembly; all addresses apply only to this dump."""
from pathlib import Path
import io,json,re,struct,sys,zipfile
BASE=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
OUT=BASE/'delphi-analysis'; lines=[]
selections={
 'delphi-dump/extbin/apps/bin/NavigationServer':[(0x1b4250,0x180),(0x21eaac,0x400),(0x1e4744,0x400),(0x22ccd8,0x500),(0x1f57e8,0x220)],
 'delphi-dump/extbin/apps/lib/libautoreceiver.so':[(0x74f50,0x124)],
}
for name,windows in selections.items():
    e=ELFFile(io.BytesIO((BASE/name).read_bytes()));segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    def read(va,n):
        for start,data in segments:
            if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
        return b''
    labels={}
    for sec in e.iter_sections():
        if sec['sh_type'] in ('SHT_DYNSYM','SHT_SYMTAB'):
            labels.update({s['st_value']:s.name for s in sec.iter_symbols() if s['st_value']})
    plt=e.get_section_by_name('.plt');rel=e.get_section_by_name('.rel.plt')
    if plt and rel:
        symbols=e.get_section(rel['sh_link'])
        for i,r in enumerate(rel.iter_relocations()):labels[plt['sh_addr']+20+12*i]=symbols.get_symbol(r['r_info_sym']).name+' [PLT]'
    md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.detail=True
    for start,size in windows:
        lines.append(f'\nFILE {name} RANGE {start:#x}+{size:#x}')
        for ins in md.disasm(read(start,size),start):
            note=''
            if ins.mnemonic in ('bl','b'):
                note=labels.get(ins.operands[0].imm,'')
            lines.append(f'{ins.address:08x} {ins.mnemonic:8s} {ins.op_str:40s} {note}')
(OUT/'targeted-disassembly.txt').write_text('\n'.join(lines),encoding='utf-8')

# Recover readable evidence from the sectionless native display ELF and IBM ROM classes.
for path in [OUT/'extracted/delphibin/DisplayManagement',OUT/'extracted/vwjxe/delphi.jxe',OUT/'extracted/vwjxe/MIBHMI.jxe']:
    data=path.read_bytes()
    if path.suffix=='.jxe':
        with zipfile.ZipFile(io.BytesIO(data)) as z:data=z.read('rom.classes')
    strings=[m.group().decode('ascii') for m in re.finditer(rb'[\x20-\x7e]{5,}',data)]
    (OUT/(path.name+'.decoded.strings.txt')).write_text('\n'.join(strings),encoding='utf-8')
    print(path.name,'readable strings',len(strings))
print('Targeted assembly:',len(lines),'lines')

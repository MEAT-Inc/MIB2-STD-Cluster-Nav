"""Read-only Android Auto receiver/application static analysis."""
from project_console import console_session, log as print
with console_session(__file__, __doc__, enabled=__name__ == '__main__'):
    from pathlib import Path
    import io,json,re,struct,sys
    BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
    from elftools.elf.elffile import ELFFile
    from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
    OUT=BASE/'delphi-analysis'; lines=[]; summaries=[]
    for name in ['AndroidAuto','libautoreceiver.so']:
     p=BASE/'delphi-dump/extbin/apps'/('bin' if name=='AndroidAuto' else 'lib')/name
     e=ELFFile(io.BytesIO(p.read_bytes())); segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
     def read(va,n):
      for start,data in segs:
       if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
      return b''
     labels={};funcs={}
     for sec in e.iter_sections():
      if sec['sh_type'] in ('SHT_DYNSYM','SHT_SYMTAB'):
       for s in sec.iter_symbols():
        if s['st_value']:
         labels[s['st_value']]=s.name
         if s['st_info']['type']=='STT_FUNC' and s['st_size']:funcs[s.name]=(s['st_value'],s['st_size'])
     plt=e.get_section_by_name('.plt');rel=e.get_section_by_name('.rel.plt')
     if plt and rel:
      sy=e.get_section(rel['sh_link'])
      for i,r in enumerate(rel.iter_relocations()):labels[plt['sh_addr']+20+i*12]=sy.get_symbol(r['r_info_sym']).name+' [PLT]'
     md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.detail=True;md.skipdata=True
     summaries.append('\nFILE '+name)
     if name=='libautoreceiver.so':
      needles=['VideoSink','ProtocolEndpoint','sendVersion','handleVersion','addEndpoint','registerEndpoint','sendServiceDiscovery','ControllerC','ControllerD','handleServiceDiscovery','getEndpoint','setVideoFocus','handleVideoFocus','handleDataAvailable']
      for n,(a,size) in funcs.items():
       if any(x in n for x in needles):summaries.append(f'{a:#x} {size:#x} {n}')
      wanted=[n for n in funcs if any(x in n for x in ['sendVersionRequest','handleVersionResponse','VideoSinkC','VideoSinkD','VideoSink13setVideoFocus','VideoSink19handleDataAvailable','VideoSink23handleVideoFocusRequest','ProtocolEndpointBaseC','Controller11addEndpoint','Controller16registerEndpoint','Controller24handleServiceDiscovery','Controller28sendServiceDiscoveryResponse','MessageRouter15registerService','GalReceiver15registerService','MediaSinkBase9ackFrames','MediaSinkBase10sendConfig','ProtocolEndpointBase15onChannelOpened','marshallProto','MessageRouter13queueOutgoing','MessageRouter24queueOutgoing','ChannelManager13queueOutgoing','ChannelManager24queueOutgoingUnencrypted','IoBufferD','shared_ptrI8IoBufferE6putRef','FrameC','FrameD','messageToFrames','marshallProto'])]
      ranges=[(n,*funcs[n]) for n in wanted]
     else:
      text=e.get_section_by_name('.text');ranges=[('all_text',text['sh_addr'],text['sh_size'])]
     for n,a,size in ranges:
      lines.append(f'\nFILE {name} FUNCTION {n} @ {a:#x} size {size:#x}')
      instructions=list(md.disasm(read(a,size),a)); indexes={ins.address:i for i,ins in enumerate(instructions)}
      for i,ins in enumerate(instructions):
       note=labels.get(ins.address,'')
       if ins.id and ins.mnemonic in ('bl','b'):
        note+=' '+labels.get(ins.operands[0].imm,'')
        if name=='AndroidAuto' and any(k in note for k in ('VideoSink','Controller','ProtocolEndpoint','addDiscovery','VideoConfig')):
         summaries.append(f'CALL {ins.address:#x} {ins.op_str}: {note}')
       lines.append(f'{ins.address:08x} {ins.mnemonic:8s} {ins.op_str:38s} {note}')
     (OUT/('android-discovery-'+name+'.assembly.txt')).write_text('\n'.join(lines),encoding='utf-8');lines=[]
    (OUT/'android-discovery-index.txt').write_text('\n'.join(summaries),encoding='utf-8')
    print('\n'.join(summaries))




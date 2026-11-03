"""Host-only TS/PSI reference validator for the observed Delphi native map format.
Never opens a network connection or writes to the vehicle. No acquired code is executed.
"""
from __future__ import annotations
from project_console import console_session, log as print
import argparse,json
from pathlib import Path

PAT_SECTION=bytes.fromhex('00b00d0000c100000001e0102d50981b')
PMT_SECTION=bytes.fromhex('02b0210001c10000f000f0001be011f00f2a077fff000005dddf28044280323ffee61f98')
NATIVE_DESCRIPTORS=bytes.fromhex('2a077fff000005dddf28044280323f')

def crc32_mpeg2(data:bytes)->int:
    value=0xffffffff
    for byte in data:
        value ^= byte<<24
        for _ in range(8):
            value=((value<<1)^0x04c11db7 if value&0x80000000 else value<<1)&0xffffffff
    return value

def psi_section(payload:bytes)->bytes:
    if not payload: raise ValueError('Empty PSI payload')
    start=1+payload[0]
    if start+3>len(payload):raise ValueError('PSI pointer exceeds payload')
    length=((payload[start+1]&15)<<8)|payload[start+2]
    section=payload[start:start+3+length]
    if len(section)!=3+length:raise ValueError('Incomplete PSI section')
    if crc32_mpeg2(section)!=0:raise ValueError('PSI CRC mismatch')
    return section

def parse_pat(section:bytes)->dict:
    if len(section)<12 or section[0]!=0 or crc32_mpeg2(section)!=0:raise ValueError('Invalid PAT')
    if (len(section)-12)%4:raise ValueError('PAT program loop length')
    programs={}
    for pos in range(8,len(section)-4,4):
        number=int.from_bytes(section[pos:pos+2],'big')
        programs[number]=int.from_bytes(section[pos+2:pos+4],'big')&0x1fff
    return {'transport_stream_id':int.from_bytes(section[3:5],'big'),'programs':programs}

def parse_pmt(section:bytes)->dict:
    if len(section)<16 or section[0]!=2 or crc32_mpeg2(section)!=0:raise ValueError('Invalid PMT')
    program_info=int.from_bytes(section[10:12],'big')&0xfff
    pos=12+program_info;streams=[]
    while pos<len(section)-4:
        if pos+5>len(section)-4:raise ValueError('Truncated PMT elementary stream')
        size=int.from_bytes(section[pos+3:pos+5],'big')&0xfff
        if pos+5+size>len(section)-4:raise ValueError('PMT descriptor out of bounds')
        streams.append({'stream_type':section[pos],'pid':int.from_bytes(section[pos+1:pos+3],'big')&0x1fff,'descriptors':section[pos+5:pos+5+size].hex()})
        pos+=5+size
    return {'program_number':int.from_bytes(section[3:5],'big'),'pcr_pid':int.from_bytes(section[8:10],'big')&0x1fff,'streams':streams}

def validate_ts(data:bytes)->dict:
    """Strict single-buffer 188-byte validator, not a complete broadcast analyzer.
    Reports native single-packet PSI. Multi-packet PSI/PES reassembly and decoder
    validity require additional tooling; no claim that a file is vehicle-ready.
    """
    if not data or len(data)%188:raise ValueError('Input must contain complete 188-byte TS packets')
    counts={};continuity={};pat=None;pmts={}
    for offset in range(0,len(data),188):
        p=data[offset:offset+188]
        if p[0]!=0x47:raise ValueError(f'TS sync missing at {offset}')
        if p[1]&0x80:raise ValueError(f'Transport error at {offset}')
        if p[3]&0xc0:raise ValueError('Scrambled payload not supported')
        pid=((p[1]&31)<<8)|p[2];afc=(p[3]>>4)&3;cc=p[3]&15;start=4;reset=False
        if not afc:raise ValueError('Reserved adaptation-field control')
        if afc&2:
            size=p[4]
            if 5+size>188:raise ValueError('Adaptation field exceeds packet')
            reset=size>0 and bool(p[5]&0x80);start=5+size
        if afc&1:
            if start>=188:raise ValueError('Payload flag without payload')
            if pid!=0x1fff and pid in continuity and not reset and cc!=((continuity[pid]+1)&15):raise ValueError(f'Payload continuity error on PID {pid:#x}')
            continuity[pid]=cc
            if p[1]&0x40 and (pid==0 or pid in (pat or {}).get('programs',{}).values()):
                section=psi_section(p[start:])
                if pid==0:pat=parse_pat(section)
                else:pmts[pid]=parse_pmt(section)
        elif reset:
            continuity.pop(pid,None)
        counts[pid]=counts.get(pid,0)+1
    return {'packet_size':188,'packets':len(data)//188,'pid_counts':counts,'pat':pat,'pmts':pmts,'limitation':'No multi-packet PSI/PES reassembly, SPS check, PCR timing analysis or vehicle compatibility validation.'}

def reference_packet(pid:int,section:bytes,cc:int=1)->bytes:
    """Construct only a host-test PSI packet from recovered fixed native bytes."""
    payload=b'\0'+section
    if len(payload)>184:raise ValueError('Reference section too large')
    return bytes([0x47,0x40|((pid>>8)&31),pid&255,0x10|(cc&15)])+payload+b'\xff'*(184-len(payload))

if __name__ == '__main__':
    with console_session(__file__, __doc__):
        p=argparse.ArgumentParser(description=__doc__);p.add_argument('--validate-ts',type=Path);args=p.parse_args()
        if args.validate_ts:result=validate_ts(args.validate_ts.read_bytes())
        else:
            result={'reference':validate_ts(reference_packet(0,PAT_SECTION)+reference_packet(0x10,PMT_SECTION)), 'pat_crc':hex(crc32_mpeg2(PAT_SECTION[:-4])),'pmt_crc':hex(crc32_mpeg2(PMT_SECTION[:-4]))}
        print(json.dumps(result,indent=2))

"""Decode read-only video configuration/discovery observations. Standard library only."""
import argparse,json,struct
from pathlib import Path
MAGIC=0x32434c44;HEADER=128;RECORD=4160;CAPACITY=32;PAYLOAD=4096

def fields(data):
    data=bytes(data)
    def var(pos):
        value=0
        for i in range(10):
            if pos>=len(data):raise ValueError('Truncated protobuf varint')
            byte=data[pos];pos+=1
            if i==9 and byte>1:raise ValueError('Protobuf varint overflow')
            value|=(byte&127)<<(i*7)
            if byte<128:return value,pos
        raise ValueError('Overlong protobuf varint')
    result=[];pos=0
    while pos<len(data):
        tag,pos=var(pos);number,wire=tag>>3,tag&7
        if not 1<=number<1<<29:raise ValueError('Invalid protobuf field')
        if wire==0:value,pos=var(pos)
        elif wire in (1,2,5):
            if wire==2:length,pos=var(pos)
            else:length=8 if wire==1 else 4
            if length>len(data)-pos:raise ValueError('Truncated protobuf value')
            value=data[pos:pos+length];pos+=length
        else:raise ValueError('Unsupported protobuf wire type')
        result.append((number,wire,value))
    return result

def describe(items):return [{'field':n,'wire':w,'value':v.hex() if isinstance(v,bytes) else v} for n,w,v in items]
def discovery(data):
    if data[:2]!=b'\x00\x06':raise ValueError('Not service discovery response')
    top=fields(data[2:]);services=[];ids=[]
    for number,wire,value in top:
        if number!=1:continue
        if wire!=2:raise ValueError('Service must be a protobuf message')
        body=fields(value);sid=[v for n,w,v in body if n==1 and w==0]
        if len(sid)!=1:raise ValueError('Missing/ambiguous service ID')
        row=dict(service_id=sid[0],fields=describe(body),media_sinks=[]);ids.extend(sid)
        for n,w,v in body:
            if n!=3 or w!=2:continue
            media=fields(v)
            row['media_sinks'].append(dict(fields=describe(media),video_configurations=[describe(fields(x)) for q,t,x in media if q==4 and t==2],
                display_id=[x for q,t,x in media if q==6 and t==0],display_type=[x for q,t,x in media if q==7 and t==0]))
        services.append(row)
    if len(set(ids))!=len(ids):raise ValueError('Duplicate advertised service IDs')
    return dict(response_fields=describe(top),services=services,advertised_service_ids=ids)

def decode(data):
    if len(data)!=HEADER+CAPACITY*RECORD:raise ValueError('Wrong display log length')
    h=struct.unpack_from('<32I',data)
    if h[:6]!=(MAGIC,1,HEADER,RECORD,CAPACITY,4) or not 0<h[6]<=0x7fffffff or h[9]!=1 or h[10]>CAPACITY or h[12] not in (0,1) or h[13] or any(h[16:]):raise ValueError('Bad/incomplete display header')
    if not h[8] or any(x<=h[8] for x in (h[7],h[14],h[15])):raise ValueError('Bad original function identities')
    records=[]
    for index in range(h[10]):
        start=HEADER+index*RECORD;r=struct.unpack_from('<16I',data,start)
        seq,event,thread,argc,caller=r[:5];args=r[5:13];length,flags,committed=r[13:]
        if seq!=index+1 or committed!=seq or event not in (1,2,3) or not 0<thread<=0x7fffffff or not caller or argc!={1:8,2:3,3:4}[event] or any(args[argc:]) or length>PAYLOAD or flags not in (0,1):raise ValueError('Bad/incomplete display record')
        payload=data[start+64:start+64+length]
        if any(data[start+64+length:start+RECORD]):raise ValueError('Nonzero unused record bytes')
        row=dict(sequence=seq,event=event,thread=thread,caller=hex(caller),object=hex(args[0]),arguments=[hex(x) for x in args[:argc]],flags=flags)
        if event in (1,2):
            if length or flags:raise ValueError('Unexpected scalar event payload')
            row['kind']='video_configuration' if event==1 else 'video_focus'
            row['integer_parameters']=[x if x<0x80000000 else x-0x100000000 for x in args[1:argc]]
        else:
            if args[1]!=0 or not args[2]:raise ValueError('Invalid control send event')
            if flags:
                if length or args[3]<=PAYLOAD:raise ValueError('Invalid oversized control candidate')
                row['kind']='oversized_control_candidate'
            else:
                if length!=args[3] or length<2:raise ValueError('Invalid discovery payload length')
                row['kind']='service_discovery';row['payload_hex']=payload.hex();row['discovery']=discovery(payload)
        records.append(row)
    if any(data[HEADER+h[10]*RECORD:]):raise ValueError('Uncommitted/unused trailing records')
    return dict(format_version=1,pid=h[6],module_base=hex(h[8]),native_offsets=dict(video_configuration=hex(h[7]-h[8]),video_focus=hex(h[14]-h[8]),queue_outgoing=hex(h[15]-h[8])),
                count=h[10],dropped=h[11],dropped_is_lower_bound=bool(h[12]),records=records)

def assess(data,registration):
    result=decode(data)
    if result['pid']!=registration['decoded_log']['pid']:raise ValueError('Display/registration PID mismatch')
    if result['native_offsets']!={'video_configuration':'0x8df74','video_focus':'0x8db50','queue_outgoing':'0x7f5d8'}:raise ValueError('Unexpected native display methods')
    trace=registration['decoded_log'];bias=registration['executable_load_bias']
    videos={int(r['endpoint'],16) for r in trace['records'] if int(r['caller'],16)-bias==0x124e54}
    configs=[r for r in result['records'] if r['event']==1 and int(r['object'],16) in videos and int(r['caller'],16)-bias==0x125014]
    packets=[r for r in result['records'] if r['kind']=='service_discovery' and int(r['caller'],16)-int(result['module_base'],16)==0x761f0]
    result.update(video_endpoints=[hex(x) for x in sorted(videos)],video_configuration_records=len(configs),discovery_records=len(packets),display_capture_validated=bool(configs and packets))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    result=json.dumps(decode(a.file.read_bytes()),indent=2)
    if a.output:a.output.write_text(result,encoding='utf-8')
    else:print(result)
if __name__=='__main__':main()

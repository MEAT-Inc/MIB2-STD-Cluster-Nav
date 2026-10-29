"""Independently review a returned display capture; offboard only, no network."""
import argparse,hashlib,json
from pathlib import Path
from run_androidauto_observer import assess
from decode_androidauto_display import assess as assess_display,fields
from android_discovery_wire_fixture import add_cluster_services,independent_decode
ROOT=Path(__file__).resolve().parents[1]
def review(folder,output):
    summary=json.loads((folder/'androidauto-summary.json').read_text());blobs={}
    for item in summary['artifacts']:
        name=item['file']
        if 'error' in item or Path(name).name!=name or name in blobs:raise ValueError('Invalid/duplicate artifact: '+name)
        data=(folder/name).read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Artifact hash/size mismatch: '+name)
        blobs[name]=data
    if not summary['actions'] or any(x['exit_code']!=0 for x in summary['actions']):raise ValueError('Remote actions failed')
    registration=assess(blobs,summary['remote_directory']);display=assess_display(blobs['display.bin'],registration)
    if not registration['capture_validated'] or not display['display_capture_validated']:raise ValueError('Required capture evidence absent')
    for filename,computed in (('observer-decoded.json',registration['decoded_log']),('display-decoded.json',display)):
        if json.loads((folder/filename).read_text())!=computed:raise ValueError('Stored decoded data disagrees: '+filename)
    base=int(display['module_base'],16);bias=registration['executable_load_bias']
    records=display['records'];packet_row=next(r for r in records if r['kind']=='service_discovery' and int(r['caller'],16)-base==0x761f0)
    packet=bytes.fromhex(packet_row['payload_hex']);services=packet_row['discovery']['services']
    video=[(s,m) for s in services for m in s['media_sinks'] if m['video_configurations']]
    if len(video)!=1 or len(video[0][1]['video_configurations'])!=1:raise ValueError('Expected one captured main-video configuration')
    sink,media=video[0];configuration=next(r for r in records if r['kind']=='video_configuration' and int(r['caller'],16)-bias==0x125014 and r['object'] in display['video_endpoints'])
    wire={f['field']:f['value'] for f in media['video_configurations'][0] if f['wire']==0}
    if [wire.get(n) for n in (1,2,3,4,5,6,8)]!=configuration['integer_parameters']:raise ValueError('Captured scalar configuration differs from wire')
    focus=[r['integer_parameters'] for r in records if r['kind']=='video_focus' and int(r['caller'],16)-bias==0x12513c and r['object']==configuration['object']]
    # Illustrative offboard IDs; absence from discovery does NOT prove empty router slots.
    pair=add_cluster_services(packet[2:],sink['service_id'],9,10,1)
    if not pair.startswith(packet[2:]):raise ValueError('Primary response altered')
    independent=independent_decode(pair);bodies=[independent_decode(v) for n,w,v in independent if n==1 and w==2]
    ids=[next(v for n,w,v in b if n==1 and w==0) for b in bodies]
    if ids!=packet_row['discovery']['advertised_service_ids']+[9,10]:raise ValueError('Candidate pair IDs incorrect')
    vfields=independent_decode(next(v for n,w,v in bodies[-2] if n==3 and w==2));ifields=independent_decode(next(v for n,w,v in bodies[-1] if n==4 and w==2))
    if (6,0,1) not in vfields or (7,0,1) not in vfields or (5,0,1) not in ifields:raise ValueError('Candidate pair display metadata mismatch')
    output.mkdir(exist_ok=True,parents=True)
    (output/'captured-discovery-main.bin').write_bytes(packet)
    (output/'captured-discovery-paired-host-only.bin').write_bytes(b'\x00\x06'+pair)
    result=dict(collection=folder.name,artifacts_verified=len(blobs),actions_verified=len(summary['actions']),completed_restored=registration['completed_restored'],observed_pid=registration['observed_pid'],restored_pid=registration['restored_pid'],manager_pid=registration['manager_pid'],registration_records=registration['decoded_log']['count'],registration_dropped=registration['decoded_log']['dropped'],display_records=display['count'],display_dropped=display['dropped'],video_endpoint=configuration['object'],configuration_arguments=configuration['integer_parameters'],configuration_matches_wire=True,discovery_bytes=len(packet),advertised_service_ids=packet_row['discovery']['advertised_service_ids'],video_service_id=sink['service_id'],advertised_video_sinks=len(video),main_display_id=media['display_id'],main_display_type=media['display_type'],focus_arguments=focus,host_only_candidate_service_ids=[9,10],host_only_candidate_bytes=2+len(pair),host_only_candidate_preserves_original=True,router_slots_verified_free=False,second_endpoints_created=False,second_stream_proven=False)
    (output/'display-capture-hardware-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--output',type=Path,default=ROOT/'delphi-analysis/control-runtime');a=p.parse_args();print(json.dumps(review(a.folder,a.output),indent=2))

"""Verify a passive phone trace and extract lifecycle evidence. Offline, stdlib only."""
import argparse,hashlib,json,re
from pathlib import Path
from run_phone_trace import assess_report
from run_androidauto_observer import fresh_stock_pid
ROOT=Path(__file__).resolve().parents[1]
def review(folder,output):
    s=json.loads((folder/'phone-trace-summary.json').read_text());blobs={}
    for a in s['artifacts']:
        if 'sha256' not in a:raise ValueError('Missing collected artifact: '+a['file'])
        b=(folder/a['file']).read_bytes()
        if len(b)!=a['bytes'] or hashlib.sha256(b).hexdigest()!=a['sha256']:raise ValueError('Artifact mismatch: '+a['file'])
        blobs[a['file']]=b
    if not s['actions'] or any(a['exit_code']!=0 for a in s['actions']):raise ValueError('Remote action failed')
    native=assess_report(blobs['trace-report.txt'],blobs['trace.bin'],s['reader_pid'])
    before=fresh_stock_pid(blobs['stock-before.txt']);after=fresh_stock_pid(blobs['stock-after.txt'])
    # PID changes and short/partial windows are diagnostic findings, not a reason
    # to discard correctly hashed trace evidence.
    ready=re.fullmatch(rb'TRACE_READER_READY pid=(\d+) seconds=180 max_bytes=16777216\r?\n',blobs['reader-ready.txt'])
    if not ready or int(ready[1])!=s['reader_pid']:raise ValueError('Readiness identity mismatch')
    if any(b'observer' in blobs[n].lower() for n in ('maps-before.txt','maps-after.txt')):raise ValueError('Observer mapping present')
    lines=blobs['trace.bin'].decode('utf8',errors='replace').splitlines();events=[(i+1,v) for i,v in enumerate(lines) if re.match(r'(?i)(androidauto|androidautoservices|appconnect):',v)]
    def matches(pattern):return [dict(line=i,text=v) for i,v in events if re.search(pattern,v,re.I)]
    selected={n:matches(pattern) for n,pattern in {'service_started':'Publishing event EV_AA_PUB_SERVICE_STARTED','configuration':'VIDEO_STREAM: codec=3, x=800, y=480, density=160','focus_pending':'Not sending video focus grant/response.*not yet available','pending_focus_sent':'Setting pending video focus to phone','focus_projected':'mode=PROJECTED','video_available':'onVideoAvailable videoAvailable=1','selected_config':'sourceVideoConfigCallback.*index=0','video_playback':'playbackStartCallback - VIDEO_STREAM: sessionId=0','codec_config':'codecConfigCallback - VIDEO_STREAM:.*len=29','shutdown':'EV_AA_SHUTDOWN|Publishing event EV_AA_PUB_SERVICE_STOPPED|AaSink::shutdown|EV_PREPARE_OFF','video_stop':'playbackStopCallback - VIDEO_STREAM'}.items()}
    startup=all(selected[k] for k in ('service_started','configuration','pending_focus_sent','focus_projected','video_available','selected_config','video_playback','codec_config'))
    result=dict(user_reported_door_black=s.get('black_after_door'),user_reported_recovery=s.get('recovered_without_reboot'),door_action_host_elapsed_seconds=s.get('door_action_host_elapsed_seconds'),door_action_in_window=s.get('door_action_within_planned_window'),collection=folder.name,verified_artifacts=len(blobs),successful_actions=len(s['actions']),reader_sha256=s['reader_sha256'],actual_unit_reader_validated=native['capture_complete'],native=native,stock_pid=before,stock_pid_unchanged=before==after,phone_view_observation=s.get('phone_view_observation'),door_opened=s.get('door_opened'),scenario=s.get('scenario','baseline'),phone_start_and_playback_captured=startup,phone_interval_evidence='startup and playback messages captured' if startup else 'insufficient lifecycle messages',display_recovery_after_fault_verified=False,cause_confirmed=False,trace_lines=len(lines),relevant_lines=len(events),lifecycle=selected)
    output.mkdir(parents=True,exist_ok=True)
    (output/(folder.name+'-review.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
    if s.get('scenario','baseline')=='baseline' and native['capture_complete'] and before==after and s.get('phone_view_observation')=='normal' and s.get('door_opened')=='n':
        (output/'phone-baseline-review.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    (output/(folder.name+'-aa-events.txt')).write_text('\n'.join(str(i)+': '+v for i,v in events),encoding='utf8');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--output',type=Path,default=ROOT/'delphi-analysis/control-runtime');a=p.parse_args();r=review(a.folder,a.output);print(json.dumps({k:v for k,v in r.items() if k!='lifecycle'},indent=2))

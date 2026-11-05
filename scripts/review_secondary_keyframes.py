"""Correlate secondary focus refreshes and independent frames; stdlib only."""
import re,struct
from secondary_timing import assess_timing
def assess_probe(timing,raw,pid,secondary):
 v=assess_timing(timing,raw,pid,secondary,probe=True);requests=[];keys=[]
 for r in v['records_detail']:
  if r['kind']==3:requests.append(r)
  elif r['kind']==2:
   chunk=raw[r['offset']:r['offset']+r['saved']]
   if any(m[1][0]&31==5 for m in re.finditer(rb'\x00\x00(?:\x00)?\x01(.)',chunk,re.S)):keys.append(r)
 responses=[]
 for r in requests:
  candidates=[k for k in keys if 0<k['monotonic_ns']-r['monotonic_ns']<=1500000000]
  responses.append(dict(request_monotonic_ns=r['monotonic_ns'],request_timestamp=r['timestamp'],fresh_keyframe_observed=bool(candidates),response_delay_ms=(candidates[0]['monotonic_ns']-r['monotonic_ns'])/1e6 if candidates else None))
 probe=secondary.get('keyframe_probe') or {}
 return dict(complete=v['complete'],focus_refresh_requests=len(requests),idr_frames=len(keys),requests_match_native_counter=len(requests)==probe.get('requests'),native_keyframes_match=len(keys)==probe.get('idr_frames'),phone_refresh_produces_fresh_idr=bool(v['complete'] and len(requests)==3 and len(requests)==probe.get('requests') and len(keys)==probe.get('idr_frames') and not probe.get('clock_error') and all(r['fresh_keyframe_observed'] for r in responses)),responses=responses,baseline_idr_frames=sum(k['monotonic_ns']<requests[0]['monotonic_ns'] for k in keys) if requests else len(keys),cluster_transport_connected=False)

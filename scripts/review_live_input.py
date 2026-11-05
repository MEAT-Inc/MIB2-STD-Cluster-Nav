"""Validate the owned live-input copy and concurrent native geometry; stdlib only."""
import hashlib,json,struct,re,statistics
from secondary_timing import assess_timing
def reader_report(b,pid):
 if len(b)!=512:raise ValueError('Live reader report size')
 w=struct.unpack('<128I',b)
 if w[:3]!=(0x3152434c,1,512) or not 0<w[3]<=0x7fffffff or w[4]!=pid or w[5] not in (0,1,2,3,4) or w[7]>2048 or w[8]>8388608 or any(w[22:]):raise ValueError('Live reader identity/layout')
 return dict(pid=w[3],source_pid=w[4],state=w[5],error=w[6],frames=w[7],bytes=w[8],queue_dropped=w[9],request_idr=bool(w[10]),stop_reason=w[19],nav_samples=w[20],nav_errors=w[21])
def nal_flags(b):
 flags=0
 for m in re.finditer(rb'\x00\x00(?:\x00)?\x01(.)',b,re.S):
  t=m[1][0]&31
  if t==5:flags|=9
  if t==1:flags|=8
  if t==7:flags|=2
  if t==8:flags|=4
 return flags
def assess_live(report,metadata,copied,source_timing,source_raw,pid,secondary):
 r=reader_report(report,pid);v=assess_timing(source_timing,source_raw,pid,secondary,probe=True)
 if len(metadata)!=32+2048*32:raise ValueError('Live timing size')
 h=struct.unpack_from('<8I',metadata)
 if h[:6]!=(0x31544c43,1,r['pid'],pid,32,2048) or h[6]!=r['frames'] or h[7] or any(metadata[32+32*h[6]:]) or len(copied)!=r['bytes']:raise ValueError('Live timing identity/accounting')
 codec=b'';expected={}
 for q in v['records_detail']:
  b=source_raw[q['offset']:q['offset']+q['saved']]
  if q['kind']==1:codec=b
  elif q['kind']==2 and b:
   key=(q['session'],q['timestamp'])
   if key in expected:raise ValueError('Ambiguous source frame timestamp')
   expected[key]=(codec+b if nal_flags(b)&1 else b,q['monotonic_ns'])
 cursor=0;exact=True;lags=[];resyncs=0;keys=0
 for i in range(h[6]):
  ts,mono,offset,n,session,flags=struct.unpack_from('<QQ4I',metadata,32+32*i)
  if offset!=cursor or not 0<n<=1048576 or offset+n>len(copied) or flags>31 or session>0x7fffffff:raise ValueError('Live frame bounds')
  b=copied[offset:offset+n];match=expected.get((session,ts))
  if flags&16:
   resyncs+=1
   if flags&7!=7:raise ValueError('Resync lacks codec/IDR')
  if i==0 and flags&7!=7:raise ValueError('First frame is dependent')
  if nal_flags(b)!=(flags&15):raise ValueError('Live NAL metadata differs')
  exact=exact and bool(match and hashlib.sha256(b).digest()==hashlib.sha256(match[0]).digest())
  if match:lags.append((mono-match[1])/1e6)
  keys+=bool(flags&1);cursor+=n
 if cursor!=len(copied):raise ValueError('Live bytes unaccounted')
 probe=secondary.get('keyframe_probe') or {}
 passed=bool(v['complete'] and r['state']==3 and not r['error'] and r['frames'] and exact and probe.get('ipc_attached') and probe.get('ipc_consumer_pid')==r['pid'] and not probe.get('ipc_error') and not probe.get('ipc_dropped') and not probe.get('ipc_malformed') and not r['queue_dropped'] and probe.get('ipc_frames')==r['frames'])
 return dict(owned_live_copy_verified=passed,frames=r['frames'],bytes=r['bytes'],all_copied_access_units_match=exact,keyframes=keys,resyncs=resyncs,queue_dropped=r['queue_dropped'],source_to_copy_median_ms=statistics.median(lags) if lags else None,source_to_copy_max_ms=max(lags) if lags else None,reader=r,cluster_transport_connected=False)
def assess_native_geometry(raw,pid,records):
 import cluster_preflight as cp
 frames=[r for r in records if r['kind']==2];samples=[]
 for line in raw.splitlines():
  if line.strip():samples.append(cp.assess_nav(line,pid))
 if any(type(s.get('monotonic_ns')) is not int or s['monotonic_ns']<=0 for s in samples):raise ValueError('Native sample clock missing')
 window=[s for s in samples if frames and frames[0]['monotonic_ns']<=s['monotonic_ns']<=frames[-1]['monotonic_ns']]
 return dict(samples=len(samples),samples_during_phone_video=len(window),active_during_phone_video=sum(s['active_geometry_observed'] for s in window),native_geometry_stayed_present=bool(window and all(s['active_geometry_observed'] for s in window)),cluster_transport_writes_measured=False)

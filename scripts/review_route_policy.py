"""Decode bounded route presentation and phone-disconnect restoration reports."""
import struct
DECISIONS={1:'deferred_projected_route',2:'forwarded_native_route',3:'unrecognized_wire_layout_or_enum',4:'bridge_not_eligible',5:'phone_instance_not_connected',6:'listener_target_or_capacity_refusal',7:'hold_deadline_expired',8:'discarded_after_phone_service_stop'}
def assess_route_policy(b,pid,nav_pid):
 w=struct.unpack('<128I',b) if len(b)==512 else ()
 if len(w)!=128 or w[0]!=0x31545052 or w[1] not in (1,2,3) or w[2:4]!=(512,pid) or w[4] not in (1,2,3,4) or w[17]>1 or w[8]+w[9]>w[7] or w[10]!=w[7] or w[7]>w[16]:raise ValueError('Route policy identity/layout')
 version=w[1];cap=12 if version==3 else 16;valid={k:v for k,v in DECISIONS.items() if version==3 or k!=8}
 if version==1 and any(w[18:]):raise ValueError('Route policy v1 reserved data')
 if version>=2 and (w[31]>cap or w[31]>w[16] or w[29]>1 or any(w[32+6*w[31]:32+6*cap]) or w[21] not in (0,*valid)):raise ValueError('Route policy trace layout')
 if version==3 and (any(w[119:]) or w[114]>1 or w[116]>16 or w[116]>w[7] or w[106]>w[16] or w[107]>w[9] or w[109]>w[11] or w[108]+w[109]>w[7] or w[117]>w[16]):raise ValueError('Route disconnect metrics')
 if w[5]:raise RuntimeError('Route presentation policy startup error '+str(w[5]))
 if w[6]!=nav_pid:raise ValueError('Route policy Nav identity')
 if version==3 and not w[114]:raise RuntimeError('Phone disconnect lifecycle profile not ready')
 v=dict(version=version,pid=w[3],state=w[4],error=w[5],nav_pid=w[6],held=w[7],released=w[8],cancelled=w[9],phone_acknowledgements=w[10],release_errors=w[11],watch_ticks=w[12],release_reason=w[13],deadline_ms=w[14]+(w[15]<<32),requests=w[16],eligible=bool(w[17]),bounded_trial=True)
 if version>=2:
  v['last_request']=dict(native_focus=w[18],app=w[19],thread=w[20],decision=valid.get(w[21],'none'),phone_instance_connected=w[22],monotonic_ms=w[23]+(w[24]<<32),nav_status=w[25],nav_error=w[26],queue_closed=w[27],queue_dropped=w[28],source_verified=bool(w[29]),payload_bytes=w[30]);v['trace']=[]
  for i in range(w[31]):
   at=32+6*i
   if w[at+5] not in valid:raise ValueError('Unknown route policy trace decision')
   v['trace'].append(dict(monotonic_ms=w[at]+(w[at+1]<<32),native_focus=w[at+2],app=w[at+3],thread=w[at+4],decision=valid[w[at+5]]))
 if version==3:v['disconnect']=dict(stopped_events=w[104],started_events=w[105],late_projected_discarded=w[106],pending_discarded=w[107],native_focus_resets=w[108],reset_errors=w[109],last_stop_monotonic_ms=w[110]+(w[111]<<32),last_publish_event=w[112],last_publish_caller=w[113],profile_verified=bool(w[114]),signature_refusals=w[115],owned_targets_remaining=w[116],native_end_forwarded=w[117],last_publish_result=w[118] if w[118]<0x80000000 else w[118]-0x100000000)
 return v

def disconnect_verified(v):
 d=v.get('disconnect',{})
 return bool(v.get('version')==3 and v.get('held',0)>0 and d.get('profile_verified') and d.get('stopped_events',0)>0 and d.get('owned_targets_remaining')==0 and not d.get('signature_refusals') and not d.get('reset_errors') and not v.get('release_errors') and (d.get('native_focus_resets',0)>0 or d.get('native_end_forwarded',0)>0))

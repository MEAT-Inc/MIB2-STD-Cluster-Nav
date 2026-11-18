"""Decode the bounded live bridge route-presentation policy report."""
import struct
DECISIONS={1:'deferred_projected_route',2:'forwarded_native_route',3:'unrecognized_wire_layout_or_enum',4:'bridge_not_eligible',5:'phone_instance_not_connected',6:'listener_target_or_capacity_refusal',7:'hold_deadline_expired'}
def assess_route_policy(b,pid,nav_pid):
 w=struct.unpack('<128I',b) if len(b)==512 else ()
 if len(w)!=128 or w[0]!=0x31545052 or w[1] not in (1,2) or w[2:4]!=(512,pid) or w[4] not in (1,2,3,4) or w[17]>1 or w[8]+w[9]>w[7] or w[10]!=w[7] or w[7]>w[16]:raise ValueError('Route policy identity/layout')
 if w[1]==1 and any(w[18:]):raise ValueError('Route policy v1 reserved data')
 if w[1]==2 and (w[31]>16 or w[31]>w[16] or w[29]>1 or any(w[32+6*w[31]:]) or w[21] not in (0,*DECISIONS)):raise ValueError('Route policy v2 trace layout')
 if w[5]:raise RuntimeError('Route presentation policy startup error '+str(w[5]))
 if w[6]!=nav_pid:raise ValueError('Route policy Nav identity')
 v=dict(version=w[1],pid=w[3],state=w[4],error=w[5],nav_pid=w[6],held=w[7],released=w[8],cancelled=w[9],phone_acknowledgements=w[10],release_errors=w[11],watch_ticks=w[12],release_reason=w[13],deadline_ms=w[14]+(w[15]<<32),requests=w[16],eligible=bool(w[17]),bounded_trial=True)
 if w[1]==2:
  v['last_request']=dict(native_focus=w[18],app=w[19],thread=w[20],decision=DECISIONS.get(w[21],'none'),phone_instance_connected=w[22],monotonic_ms=w[23]+(w[24]<<32),nav_status=w[25],nav_error=w[26],queue_closed=w[27],queue_dropped=w[28],source_verified=bool(w[29]),payload_bytes=w[30]);v['trace']=[]
  for i in range(w[31]):
   at=32+6*i
   if w[at+5] not in DECISIONS:raise ValueError('Unknown route policy trace decision')
   v['trace'].append(dict(monotonic_ms=w[at]+(w[at+1]<<32),native_focus=w[at+2],app=w[at+3],thread=w[at+4],decision=DECISIONS[w[at+5]]))
 return v

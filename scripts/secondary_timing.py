"""Validate bounded callback records against captured raw bytes, using only stdlib."""
import statistics,struct
CAPACITY=2048
SIZE=32+40*CAPACITY
def assess_timing(data,raw,pid,secondary,probe=False):
 if len(data)!=SIZE:raise ValueError('Timing file size mismatch')
 h=struct.unpack_from('<8I',data)
 if h[:5]!=(0x314d4954,1,pid,40,CAPACITY) or h[5]>CAPACITY:raise ValueError('Timing capture identity/layout mismatch')
 records=[];cursor=0
 for i in range(h[5]):
  kind,session,ts,mono,offset,requested,saved,reserved=struct.unpack_from('<IIQQ4I',data,32+40*i)
  if kind not in ((1,2,3) if probe else (1,2)) or kind==3 and (requested or saved) or reserved or requested>(65536 if kind==1 else 1048576) or saved>requested or offset!=cursor or offset+saved>len(raw):raise ValueError('Timing record bounds/accounting mismatch')
  if records and mono<records[-1]['monotonic_ns']:raise ValueError('Local timing regressed')
  records.append(dict(kind=kind,session=session,timestamp=ts,monotonic_ns=mono,offset=offset,requested=requested,saved=saved));cursor+=saved
 if any(data[32+40*h[5]:]):raise ValueError('Timing unused records not zero')
 frames=[v for v in records if v['kind']==2];codec=[v for v in records if v['kind']==1]
 good=bool(frames and codec and not h[6] and not h[7] and cursor==len(raw) and all(v['saved']==v['requested'] for v in records) and len(frames)==secondary['frames'] and sum(v['saved'] for v in codec)==secondary['codec_saved_bytes'])
 deltas=[b['timestamp']-a['timestamp'] for a,b in zip(frames,frames[1:]) if not probe or a['session']==b['session']];arrival=(frames[-1]['monotonic_ns']-frames[0]['monotonic_ns'])/1e9 if len(frames)>1 else 0
 span=frames[-1]['timestamp']-frames[0]['timestamp'] if len(frames)>1 else 0
 ratio=span/arrival if arrival>0 else None
 good=good and not any(v<0 for v in deltas) and all(v['monotonic_ns']>0 and (v['kind'] not in (2,3) or (0<=v['session']<=0x7fffffff if probe else v['session']==secondary.get('session',v['session']))) for v in records)
 return dict(complete=good,records=len(records),frames=len(frames),codec_records=len(codec),dropped_records=h[6],clock_error=h[7],raw_bytes_accounted=cursor,arrival_span_seconds=arrival,source_timestamp_span=span,source_timestamp_delta_min=min(deltas) if deltas else None,source_timestamp_delta_median=statistics.median(deltas) if deltas else None,source_timestamp_delta_max=max(deltas) if deltas else None,source_timestamp_regressed=any(v<0 for v in deltas),source_units_per_arrival_second=ratio,timestamp_units_confirmed=False,records_detail=records)

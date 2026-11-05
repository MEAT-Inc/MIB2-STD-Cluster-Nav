"""Prepare and verify frequent-keyframe AA replay offline; never connects to the radio."""
from pathlib import Path
from project_console import console_session, log as print, status
import sys,io,json,struct,hashlib,math,itertools
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.tools/video-python'),str(ROOT/'.tools/python')]
import av,numpy as np
from cluster_ts_mux import ClusterTSMux
from native_transport_packet_reference import validate_ts
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 source=ROOT/'delphi-dump/_disconnect_observer_20261103_022700_3b445220'
 review=json.loads((ROOT/'delphi-analysis/cluster-bridge/20261103-review/video-review.json').read_text())
 raw=(source/'secondary.h264').read_bytes();assert sha(raw)==review['source_sha256']
 data=(source/'timing.bin').read_bytes();rows=[struct.unpack_from('<IIQQ4I',data,32+40*i) for i in range(struct.unpack_from('<I',data,20)[0])];frames=[r for r in rows if r[0]==2];ms=[(r[2]-frames[0][2])//1000 for r in frames];assert len(ms)==617 and all(a<b for a,b in zip(ms,ms[1:]));ms=[t for t in ms if t<=20000];frame_count=len(ms)
 e=av.CodecContext.create('libx264','w');e.width=800;e.height=480;e.pix_fmt='yuv420p';e.time_base=Fraction(1,90000);e.framerate=Fraction(15,1);e.gop_size=5;e.max_b_frames=0;e.thread_count=2
 e.options={'preset':'veryfast','tune':'zerolatency','profile':'baseline','level':'3.1','crf':'18','x264-params':'keyint=5:min-keyint=5:scenecut=0:bframes=0:ref=1:repeat-headers=1:annexb=1:force-cfr=0'}
 status('Encoding '+str(frame_count)+' map frames with a keyframe every five frames.');packets=[];count=0
 with av.open(io.BytesIO(raw),format='h264') as c:
  color={name:getattr(c.streams.video[0].codec_context,name) for name in ('color_range','colorspace','color_primaries','color_trc')}
  for name,value in color.items():setattr(e,name,value)
  status('Preserving source color metadata: '+str(color))
  for i,f in enumerate(c.decode(video=0)):
   if i>=frame_count:break
   f.pts=ms[i]*90;f.time_base=Fraction(1,90000);packets.extend(e.encode(f));count+=1
 packets.extend(e.encode(None));assert count==frame_count and len(packets)==frame_count
 chunks=[bytes(p) for p in packets];assert [p.pts for p in packets]==[t*90 for t in ms]
 keyframes=[i for i,p in enumerate(packets) if p.is_keyframe];assert keyframes==list(range(0,frame_count,5))
 encoded=b''.join(chunks);a=av.open(io.BytesIO(raw),format='h264');b=av.open(io.BytesIO(encoded),format='h264');codec=b.streams.video[0].codec_context
 assert codec.name=='h264' and codec.profile in ('Baseline','Constrained Baseline') and (codec.width,codec.height)==(800,480),(codec.name,codec.profile,codec.width,codec.height)
 status('Checking decoded frame count, image quality and timing.');psnr=[];hashes=[];decoded=0
 for original,new in zip(itertools.islice(a.decode(video=0),frame_count),b.decode(video=0),strict=True):
  x=original.to_ndarray(format='rgb24');y=new.to_ndarray(format='rgb24');delta=x.astype(np.float32)-y.astype(np.float32);mse=float(np.mean(delta*delta));psnr.append(99.0 if not mse else 10*math.log10(255*255/mse));hashes.append(sha(y.tobytes()));decoded+=1
 assert decoded==frame_count and min(psnr)>=35,(decoded,min(psnr))
 groups=[];clock=0
 def emit(p):
  if not groups or groups[-1][0]!=clock:groups.append([clock,bytearray()])
  groups[-1][1].extend(p);return len(p)
 mux=ClusterTSMux(emit);tick=0
 for t,au in zip(ms,chunks):
  while tick<t:clock=tick;mux.tick(clock);tick+=16
  clock=t;assert mux.push(au,clock)
 ts=b''.join(p for _,p in groups);transport=validate_ts(ts)
 with av.open(io.BytesIO(ts),format='mpegts') as c:
  output=[(sha(f.to_ndarray(format='rgb24').tobytes()),f.pts) for f in c.decode(video=0)]
 assert [h for h,t in output]==hashes and [t for h,t in output]==[t*90+1 for t in ms]
 body=b''.join(struct.pack('<II',t,len(p))+p for t,p in groups);replay=struct.pack('<8I',0x314c5052,1,len(body)+32,len(groups),len(ts)//188,groups[-1][0],0,0)+body
 out=ROOT/'delphi-analysis/cluster-bridge/20261104-keyframe-replay';out.mkdir(exist_ok=True)
 (out/'secondary-keyframes.h264').write_bytes(encoded);(out/'replay-keyframes.bin').write_bytes(replay)
 metadata=dict(source_sha256=sha(raw),encoded_sha256=sha(encoded),replay_sha256=sha(replay),encoded_bytes=len(encoded),replay_bytes=len(replay),fits_current_8MiB_limit=len(replay)<=8388608,decoded_frames=decoded,original_source_frames=617,excerpt_limit_ms=20000,dimensions=[800,480],profile='Baseline',color_metadata=color,level='3.1',keyframe_interval_frames=5,keyframe_count=len(keyframes),keyframe_indices=keyframes,original_frame_times_ms=ms,minimum_rgb_psnr_db=min(psnr),average_rgb_psnr_db=sum(psnr)/len(psnr),pixels_reencoded=True,transport=transport,on_car_tested=False)
 (out/'review.json').write_text(json.dumps(metadata,indent=2));print(json.dumps({k:v for k,v in metadata.items() if k not in ('keyframe_indices','original_frame_times_ms','transport')},indent=2))
if __name__=='__main__':
 with console_session(__file__, __doc__):
  main()

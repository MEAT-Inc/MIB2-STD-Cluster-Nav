"""Verify native streaming packets against the proven mux and captured phone pixels. Offline only."""
from project_console import console_session,status,log as print
from pathlib import Path
import hashlib,io,json,struct,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
from cluster_ts_mux import ClusterTSMux
from native_transport_packet_reference import validate_ts
from review_live_input import nal_flags

def main():
 source=ROOT/'delphi-dump/_disconnect_observer_20261110_133825_56032b20'
 out=ROOT/'delphi-analysis/cluster-bridge/20261110-live-input-review';out.mkdir(parents=True,exist_ok=True)
 raw=(source/'secondary.h264').read_bytes();timing=(source/'timing.bin').read_bytes()
 rows=[struct.unpack_from('<IIQQ4I',timing,32+40*i) for i in range(struct.unpack_from('<I',timing,20)[0])]
 first=next(r[2] for r in rows if r[0]==2);codec=b'';input_data=bytearray();packets=[];count=0;tick=0
 mux=ClusterTSMux(lambda b:packets.append(b) or len(b))
 for q in rows:
  kind,session,ts,mono,offset,n,saved,reserved=q
  part=raw[offset:offset+saved]
  if kind==1:codec=part
  if kind!=2:continue
  au=codec+part if nal_flags(part)&1 else part;ms=(ts-first)//1000;flags=nal_flags(au)|(16 if not count else 0)
  input_data.extend(struct.pack('<QII',ms,len(au),flags)+au)
  while tick<ms:mux.tick(tick);tick+=32
  assert mux.push(au,ms);count+=1
 inp=out/'mux-input.bin';actual=out/'native-live.ts';inp.write_bytes(input_data)
 status('Checking all '+str(count)+' phone frames through native streaming packetizer.')
 cmd=['docker','run','--rm','--network','none','-v',str(ROOT)+':/src','delphi-qnx65:qemu','/src/native/cluster-bridge/live/build/live_mux_host','/src/'+inp.relative_to(ROOT).as_posix(),'/src/'+actual.relative_to(ROOT).as_posix()]
 result=subprocess.run(cmd,capture_output=True,text=True)
 if result.returncode:raise ValueError('Native mux failed: '+result.stdout+result.stderr)
 data=actual.read_bytes();expected=b''.join(packets)
 if data!=expected:raise ValueError('Native packet stream differs from independently generated reference')
 transport=validate_ts(data)
 sys.path.insert(0,str(ROOT/'.tools/video-python'))
 import av
 def decoded(b,fmt):
  with av.open(io.BytesIO(b),format=fmt) as c:
   return [(f.width,f.height,hashlib.sha256(f.to_ndarray(format='yuv420p').tobytes()).hexdigest()) for f in c.decode(video=0)]
 status('Checking decoded picture identity after native packetization.')
 pictures=decoded(raw,'h264');converted=decoded(data,'mpegts')
 if len(pictures)!=count or pictures!=converted:raise ValueError('Native mux lost or changed decoded phone pictures')
 review=dict(source_collection=source.name,source_frames=count,native_packetizer_matches_reference=True,decoded_frames=len(pictures),decoded_pixels_unchanged=True,dimensions=list(pictures[0][:2]),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),transport=transport,live_queue_on_car_verified=False,cluster_transport_connected=False)
 (out/'native-mux-review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()

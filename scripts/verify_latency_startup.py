"""Verify gradual catchup timing and unchanged pictures against the latest car capture."""
from project_console import console_session,status,log as print
from pathlib import Path
import sys,struct,hashlib,json,subprocess,io
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'delphi-dump/_disconnect_observer_20261118_201524_1f980346'
 out=ROOT/'delphi-analysis/cluster-bridge/20261118-v12-latency-review';out.mkdir(parents=True,exist_ok=True)
 raw=(source/'live-copy.h264').read_bytes();meta=(source/'live-copy-timing.bin').read_bytes()
 count=struct.unpack_from('<I',meta,24)[0];assert count==539
 rows=[struct.unpack_from('<QQ4I',meta,32+32*i) for i in range(count)];origin=rows[0][1]
 arrivals=[(r[1]-origin)//1000000 for r in rows]
 scheduled=b''.join(struct.pack('<QII',t,r[3],r[5])+raw[r[2]:r[2]+r[3]] for t,r in zip(arrivals,rows))
 (out/'input.bin').write_bytes(scheduled)
 command='''set -e
/usr/bin/gcc -B/usr/bin/ -std=gnu11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer /src/native/cluster-bridge/live/startup.c /src/native/cluster-bridge/live/mux.c /src/native/cluster-bridge/live/startup-file.c -o /tmp/live-startup
/tmp/live-startup /src/delphi-analysis/cluster-bridge/20261118-v12-latency-review/input.bin /src/delphi-analysis/cluster-bridge/20261118-v12-latency-review/output.ts
'''
 status('Checking all captured pictures and gradual catchup under sanitizers.')
 v=subprocess.run(['docker','run','--rm','--network','none','-v',str(ROOT)+':/src','delphi-qnx65:qemu','sh','-c',command],capture_output=True,text=True)
 if v.returncode:raise RuntimeError(v.stdout+v.stderr)
 sys.path.insert(0,str(ROOT/'.tools/video-python'));import av
 def decode(data,fmt):
  with av.open(io.BytesIO(data),format=fmt) as c:
   return [(f.width,f.height,hashlib.sha256(f.to_ndarray(format='yuv420p').tobytes()).hexdigest(),f.pts) for f in c.decode(video=0)]
 original=decode(raw,'h264');actual=decode((out/'output.ts').read_bytes(),'mpegts')
 assert len(original)==count and [x[:3] for x in actual]==[original[0][:3]]*3+[x[:3] for x in original]
 due=[1000+t*4//5 if t<3750 else t+250 for t in arrivals]
 expected_pts=[t*90+1 for t in [0,333,666]+due]
 assert [x[3] for x in actual]==expected_pts,([x[3] for x in actual[:6]],expected_pts[:6])
 assert all(250<=d-t<=1000 for d,t in zip(due,arrivals))
 assert all(d-t==250 for d,t in zip(due,arrivals) if t>=3750)
 report=dict(source=source.name,source_frames=count,output_frames=len(actual),bootstrap_frames=3,
  all_original_frames_and_pixels_preserved=True,source_order_preserved=True,frame_pts_follow_schedule=True,
  reencoded=False,sanitizers_passed=True,initial_delay_ms=1000,steady_delay_ms=250,
  catchup_pace_numerator=4,catchup_pace_denominator=5,catchup_finished_at_ms=4000,
  decoder_hardware_tested=False,source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('native/cluster-bridge/live/startup.c','native/cluster-bridge/live/startup.h','native/cluster-bridge/live/mux.c')})
 (out/'startup-review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()

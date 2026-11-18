"""Verify buffered startup against all captured live pictures; offline only."""
from project_console import console_session,status,log as print
from pathlib import Path
import sys,struct,hashlib,json,subprocess,io
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'delphi-dump/_disconnect_observer_20261118_125442_314326f0';out=ROOT/'delphi-analysis/cluster-bridge/20261118-v6-decoder-review';out.mkdir(exist_ok=True,parents=True)
 raw=(p/'live-copy.h264').read_bytes();meta=(p/'live-copy-timing.bin').read_bytes();count=struct.unpack_from('<I',meta,24)[0];rows=[struct.unpack_from('<QQ4I',meta,32+32*i) for i in range(count)];origin=rows[0][1]
 data=b''.join(struct.pack('<QII',(mono-origin)//1000000,n,flags)+raw[offset:offset+n] for ts,mono,offset,n,session,flags in rows);(out/'startup-input.bin').write_bytes(data)
 status('Checking native startup buffer with captured phone frames under sanitizers.')
 command='set -e\n/usr/bin/gcc -B/usr/bin/ -std=gnu11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer /src/native/cluster-bridge/live/startup.c /src/native/cluster-bridge/live/mux.c /src/native/cluster-bridge/live/startup-file.c -o /tmp/live-startup\n/tmp/live-startup /src/delphi-analysis/cluster-bridge/20261118-v6-decoder-review/startup-input.bin /src/delphi-analysis/cluster-bridge/20261118-v6-decoder-review/startup-output.ts'
 v=subprocess.run(['docker','run','--rm','--network','none','-v',str(ROOT)+':/src','delphi-qnx65:qemu','sh','-c',command.replace('\\n','\n')],capture_output=True,text=True)
 if v.returncode:raise RuntimeError(v.stdout+v.stderr)
 print(v.stdout.strip());sys.path.insert(0,str(ROOT/'.tools/video-python'));import av
 def decode(b,fmt):
  with av.open(io.BytesIO(b),format=fmt) as c:return [(f.width,f.height,hashlib.sha256(f.to_ndarray(format='yuv420p').tobytes()).hexdigest()) for f in c.decode(video=0)]
 original=decode(raw,'h264');actual=decode((out/'startup-output.ts').read_bytes(),'mpegts');assert len(original)==405 and actual==[original[0]]*3+original
 report=dict(source=p.name,source_frames=405,output_frames=len(actual),bootstrap_frames=3,all_original_frames_and_pixels_preserved=True,source_order_preserved=True,reencoded=False,delay_ms=1000,sanitizers_passed=True,native_metrics=v.stdout.strip(),source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('native/cluster-bridge/live/startup.c','native/cluster-bridge/live/startup.h','native/cluster-bridge/live/mux.c')})
 (out/'startup-review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()

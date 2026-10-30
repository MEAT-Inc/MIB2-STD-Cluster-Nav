"""Offline verification/decoding of a secondary capture; never connects to the car."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/video-python'))
def digest(b):return hashlib.sha256(b).hexdigest()
def inspect(folder,out):
 folder=folder.resolve();out=out.resolve()
 import av
 import run_disconnected_observer as observer
 summary=json.loads((folder/'disconnect-summary.json').read_text())
 blobs={}
 for record in summary['artifacts']:
  name=record['file']
  if Path(name).name!=name:raise ValueError('Artifact path escapes collection')
  b=(folder/name).read_bytes()
  if len(b)!=record['bytes'] or digest(b)!=record['sha256']:raise ValueError('Artifact integrity: '+name)
  blobs[name]=b
 blobs['launch.txt']=blobs['start.txt']+b'\n'+blobs['cleanup.txt']
 control=observer.assess_final(blobs,summary['remote_directory'],summary['capture_profile_seconds'])
 factory=observer.assess_factory(blobs['factory.bin'],control['observed_pid'],control['executable_load_bias'],control['decoded_log'])
 stream=observer.assess_secondary(blobs['secondary.bin'],blobs['secondary.h264'],control['observed_pid'],int.from_bytes(blobs['factory.bin'][40:44],'little'))
 if not stream['secondary_trial_passed']:raise ValueError('Secondary stream evidence failed')
 out.mkdir(parents=True,exist_ok=True)
 frames=[];keys=[];pictures={};image_paths=[]
 with av.open(str(folder/'secondary.h264'),format='h264') as container:
  profile=container.streams.video[0].codec_context.profile
  for i,f in enumerate(container.decode(video=0)):
   rgb=f.to_ndarray(format='rgb24');frames.append(digest(rgb.tobytes()))
   pictures[str(f.pict_type)]=pictures.get(str(f.pict_type),0)+1
   if f.key_frame:keys.append(i)
   if i in (0,180,370):
    p=out/('frame-%04d.png'%i);f.to_image().save(p);image_paths.append(p.relative_to(ROOT).as_posix())
   size=[f.width,f.height];pixel=f.format.name
 if not frames:raise ValueError('No decoded frames')
 # Offline transport fixture uses an explicit synthetic cadence, never a measured claim.
 from cluster_ts_mux import ClusterTSMux
 from native_transport_packet_reference import validate_ts
 output=bytearray()
 def sink(packet):output.extend(packet);return len(packet)
 mux=ClusterTSMux(sink);access_units=[];next_tick=0
 with av.open(str(folder/'secondary.h264'),format='h264') as source:
  for packet in source.demux(video=0):
   if not packet.size:continue
   au=bytes(packet);ms=len(access_units)*1000//30
   while next_tick<ms:mux.tick(next_tick);next_tick+=16
   if not mux.push(au,ms):raise ValueError('Parsed stream did not start at IDR')
   access_units.append(au)
 transport=out/'transport-fixture.ts';transport.write_bytes(output)
 wire=validate_ts(output)
 # Independent payload reassembly verifies every AVC byte survives the mux.
 pes=[]
 for offset in range(0,len(output),188):
  q=output[offset:offset+188];pid=((q[1]&31)<<8)|q[2];afc=(q[3]>>4)&3
  if pid!=0x11 or not afc&1:continue
  start=5+q[4] if afc&2 else 4
  if q[1]&64:pes.append(bytearray())
  if not pes:raise ValueError('Missing PES start')
  pes[-1].extend(q[start:])
 if [bytes(v[19:]) for v in pes]!=access_units:raise ValueError('Remux changed AVC access units')
 remux_hashes=[]
 with av.open(str(transport),format='mpegts') as decoded:
  for f in decoded.decode(video=0):remux_hashes.append(digest(f.to_ndarray(format='rgb24').tobytes()))
 if remux_hashes!=frames:raise ValueError('Remuxed frames differ from source')

 report=dict(collection=folder.name,verified_artifacts=len(summary['artifacts']),control_restored=control['process_restoration_verified'],secondary=stream,source_sha256=digest(blobs['secondary.h264']),decoded_frames=len(frames),dimensions=size,pixel_format=pixel,profile=profile,keyframe_indices=keys,picture_types=pictures,decoded_rgb_sha256=frames,preview_files=image_paths,timing='Raw capture lacks per-access-unit timestamps; demuxer guessed frame rate is not a measurement.',cluster_decoder_tested=False,mux_source_sha256=digest((ROOT/'scripts/cluster_ts_mux.py').read_bytes()),offline_remux=dict(file=transport.relative_to(ROOT).as_posix(),bytes=len(output),sha256=digest(output),access_units=len(access_units),decoded_pixels_identical=True,synthetic_fps=30,original_timing_preserved=False,wire=wire))
 (out/'video-review.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k not in ('decoded_rgb_sha256','secondary')},indent=2))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('collection',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();inspect(a.collection,a.output)

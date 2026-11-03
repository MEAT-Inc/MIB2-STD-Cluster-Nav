"""Offline verification/decoding of a secondary capture; never connects to the car."""
from project_console import console_session, log as print
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/video-python'))
def digest(b):return hashlib.sha256(b).hexdigest()
def inspect(folder,out,recorded_microseconds=False):
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
 mux=ClusterTSMux(sink);access_units=[];next_tick=0;timing_review=None;recorded_frames=[]
 if recorded_microseconds:
  from secondary_timing import assess_timing
  timing_review=assess_timing(blobs['timing.bin'],blobs['secondary.h264'],control['observed_pid'],stream)
  if not timing_review['complete'] or timing_review['source_timestamp_regressed']:raise ValueError('Incomplete/regressed timing cannot drive remux')
  if not 950000<timing_review['source_units_per_arrival_second']<1050000:raise ValueError('Captured clock does not corroborate microseconds')
  details=timing_review.pop('records_detail');recorded_frames=[v for v in details if v['kind']==2]
  codec=[v for v in details if v['kind']==1]
  if len(codec)!=1 or codec[0]['offset']!=0:raise ValueError('Changed codec needs explicit access-unit assembly')
  first_timestamp=recorded_frames[0]['timestamp']
  timing_review.update(timestamp_unit_used='microseconds',unit_basis='Explicit review choice corroborated by phone/local clock ratio; not a protocol-spec assertion')

 with av.open(str(folder/'secondary.h264'),format='h264') as source:
  for packet in source.demux(video=0):
   if not packet.size:continue
   au=bytes(packet);index=len(access_units)
   if recorded_microseconds:
    record=recorded_frames[index];raw=blobs['secondary.h264'];expected=raw[record['offset']:record['offset']+record['saved']]
    if index==0:expected=raw[:codec[0]['saved']]+expected
    if au!=expected:raise ValueError('Callback boundary is not one parsed access unit')
    ms=(record['timestamp']-first_timestamp)//1000
   else:ms=index*1000//30
   while next_tick<ms:mux.tick(next_tick);next_tick+=16
   if not mux.push(au,ms):raise ValueError('Parsed stream did not start at IDR')
   access_units.append(au)
 if recorded_microseconds and len(access_units)!=len(recorded_frames):raise ValueError('Timing/access-unit count differs')
 transport=out/('transport-recorded-timing.ts' if recorded_microseconds else 'transport-fixture.ts');transport.write_bytes(output)
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

 report=dict(collection=folder.name,verified_artifacts=len(summary['artifacts']),control_restored=control['process_restoration_verified'],secondary=stream,source_sha256=digest(blobs['secondary.h264']),decoded_frames=len(frames),dimensions=size,pixel_format=pixel,profile=profile,keyframe_indices=keys,picture_types=pictures,decoded_rgb_sha256=frames,preview_files=image_paths,timing=timing_review if recorded_microseconds else 'Raw capture lacks per-access-unit timestamps; demuxer guessed frame rate is not a measurement.',cluster_decoder_tested=False,mux_source_sha256=digest((ROOT/'scripts/cluster_ts_mux.py').read_bytes()),offline_remux=dict(file=transport.relative_to(ROOT).as_posix(),bytes=len(output),sha256=digest(output),access_units=len(access_units),decoded_pixels_identical=True,synthetic_fps=None if recorded_microseconds else 30,original_timing_preserved=recorded_microseconds,timestamp_quantization_ms=1 if recorded_microseconds else None,wire=wire))
 (out/'video-review.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k not in ('decoded_rgb_sha256','secondary')},indent=2))
 return report
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        p=argparse.ArgumentParser(description=__doc__);p.add_argument('collection',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--recorded-microseconds',action='store_true');a=p.parse_args();inspect(a.collection,a.output,a.recorded_microseconds)

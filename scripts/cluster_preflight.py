"""Fixed unit identity and read-only native-encoder snapshot validation."""
import hashlib,json,re
NAV_BYTES=4909668
NAV_SHA='a999725350df8503c44a25da2676a8c1a99914a99a36f24bb6334a509def4afe'
def nav_pid(data):
 rows=[]
 for line in data.decode('ascii').splitlines():
  m=re.fullmatch(r'\s*(\d+)\s+((?:/extbin/apps/bin/)?NavigationServer)\s+-fcfg\s+\.\./cfg/NAV/v0/NC/Delphi/NavServer\.cfg(?:\s+-X\d{1,20})?\s*',line)
  if m:rows.append(int(m[1]))
 if len(rows)!=1 or not 0<rows[0]<=0x7fffffff:raise ValueError('Expected one stock NavigationServer with known arguments')
 return rows[0]
def verify_navigation(data):
 if len(data)!=NAV_BYTES or hashlib.sha256(data).hexdigest()!=NAV_SHA:raise ValueError('NavigationServer firmware differs')
def assess_nav(data,pid):
 v=json.loads(data)
 if v.get('version')!=1 or v.get('pid')!=pid or v.get('readonly') is not True or v.get('stable') is not True or v.get('load_bias')!=0 or not 0<v.get('parent',0)<=0x7fffffff or not 0<v.get('start_time',0):raise ValueError('Native snapshot identity/state mismatch')
 for name in ('encoder','rate_candidate','width','height','buffer_width','buffer_height','padding'):
  if type(v.get(name)) is not int or not 0<=v[name]<=0xffffffff:raise ValueError('Native snapshot numeric bounds')
 if type(v.get('writer_fd')) is not int or not -1<=v['writer_fd']<65536:raise ValueError('Native writer descriptor invalid')
 geometry=bool(v['encoder'] and v['writer_fd']>=0 and 0<v['width']<=4096 and 0<v['height']<=4096 and v['width']<=v['buffer_width']<=8192 and v['height']<=v['buffer_height']<=8192 and v['padding']<=8192)
 return dict(**v,active_geometry_observed=geometry,dimensions=[v['width'],v['height']] if geometry else None,cluster_decoder_tested=False)

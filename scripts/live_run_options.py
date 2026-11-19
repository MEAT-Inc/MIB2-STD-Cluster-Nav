"""Token-bound live-run limits for the native sink and route observer; stdlib only."""
import re,struct
MAGIC=0x314f564c
def options_bytes(token,seconds):
 if not re.fullmatch('[0-9a-f]{32}',token) or seconds not in (0,30):raise ValueError('Invalid live-run options')
 return struct.pack('<8I',MAGIC,1,32,seconds,*(int(token[i:i+8],16) for i in range(0,32,8)))
def add_live_arguments(parser):
 group=parser.add_mutually_exclusive_group()
 group.add_argument('--no-live-timeout',dest='live_seconds',action='store_const',const=0,default=None,help='Live cluster output until phone disconnect; diagnostic capture remains bounded')
 group.add_argument('--live-seconds',dest='live_seconds',type=int,choices=(30,),help='Use the bounded 30-second live cluster trial (default)')

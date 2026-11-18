/* Secondary-only layout profiles; baseline observer still uses wire.c directly. */
#define cluster_wire_rewrite layout_metadata_rewrite
#include "../../secondary-display/wire.c"
#undef cluster_wire_rewrite
#ifndef MARGIN_WIDTH_PIXELS
#define MARGIN_WIDTH_PIXELS 200
#endif
#if MARGIN_WIDTH_PIXELS < 0 || MARGIN_WIDTH_PIXELS > 320 || MARGIN_WIDTH_PIXELS % 2
#error Invalid symmetric width margin
#endif
#ifndef LAYOUT_DENSITY_DPI
#define LAYOUT_DENSITY_DPI 160
#endif
#if LAYOUT_DENSITY_DPI != 140 && LAYOUT_DENSITY_DPI != 160
#error Unsupported secondary layout density
#endif
#ifndef LAYOUT_UI_INSET_PIXELS
#define LAYOUT_UI_INSET_PIXELS 0
#endif
#ifndef LAYOUT_UI_BOTTOM_INSET_PIXELS
#define LAYOUT_UI_BOTTOM_INSET_PIXELS 0
#endif
#if LAYOUT_UI_BOTTOM_INSET_PIXELS < 0 || LAYOUT_UI_BOTTOM_INSET_PIXELS > 160
#error Invalid bottom UI inset
#endif
#if LAYOUT_UI_BOTTOM_INSET_PIXELS && !LAYOUT_UI_INSET_PIXELS
#error Bottom inset requires the UI inset profile
#endif
#if LAYOUT_UI_INSET_PIXELS < 0 || LAYOUT_UI_INSET_PIXELS > 320
#error Invalid UI inset
#endif
#if LAYOUT_UI_INSET_PIXELS && (MARGIN_WIDTH_PIXELS || LAYOUT_DENSITY_DPI != 140)
#error UI inset profile requires zero video margins and density 140
#endif
#if MARGIN_WIDTH_PIXELS || LAYOUT_DENSITY_DPI != 160 || LAYOUT_UI_INSET_PIXELS
struct LayoutWorkspace {unsigned char baseline[16384],service[8192],media[4096],config[1024];};
static int layout_config(Writer *out,const Field *cfg){unsigned pos=0,seen[9]={0};Field f;while(pos<cfg->len){if(!next(cfg->data,cfg->len,&pos,&f))return 0;if(LAYOUT_UI_INSET_PIXELS && f.number==11)return 0;if(f.number==1||f.number==2||f.number==3||f.number==4||f.number==5||f.number==8){if(f.wire||++seen[f.number]!=1)return 0;if((f.number==1&&f.value!=1)||(f.number==2&&f.value!=2)||(f.number==3&&f.value)||(f.number==4&&f.value)||(f.number==5&&f.value!=160)||(f.number==8&&f.value!=10000))return 0;}if(f.number==3){if(!putvar(out,24)||!putvar(out,MARGIN_WIDTH_PIXELS))return 0;}else if(f.number==5){if(!putvar(out,40)||!putvar(out,LAYOUT_DENSITY_DPI))return 0;}else if(!put(out,f.raw,f.size))return 0;}if(!(seen[1]&&seen[2]&&seen[3]&&seen[4]&&seen[5]&&seen[8]))return 0;
#if LAYOUT_UI_INSET_PIXELS
/* UiConfig content/stable insets are distinct from encoded-video margins.
 * Schema: borconi/obd2aa 5768e939, app/src/main/proto/protos.proto.
 * Phone interpretation must be verified on the target AA version. */
{unsigned char edges[32],config[80];Writer inset={edges,0,sizeof edges},ui={config,0,sizeof config};
if(!putvar(&inset,8)||!putvar(&inset,0)||!putvar(&inset,16)||!putvar(&inset,LAYOUT_UI_BOTTOM_INSET_PIXELS)||!putvar(&inset,24)||!putvar(&inset,LAYOUT_UI_INSET_PIXELS)||!putvar(&inset,32)||!putvar(&inset,LAYOUT_UI_INSET_PIXELS)||!message(&ui,2,&inset)||!message(&ui,3,&inset)||!message(out,11,&ui))return 0;}
#endif
return 1;}
static int layout_media(Writer *out,const Field *media,struct LayoutWorkspace *work){unsigned pos=0,count=0;Field f;Writer cfg={work->config,0,sizeof work->config};while(pos<media->len){if(!next(media->data,media->len,&pos,&f))return 0;if(f.number==4){if(f.wire!=2||++count!=1||!layout_config(&cfg,&f)||!message(out,4,&cfg))return 0;}else if(!put(out,f.raw,f.size))return 0;}return count==1;}
static int layout_service(Writer *out,const Field *svc,struct LayoutWorkspace *work){unsigned pos=0,count=0;Field f;Writer media={work->media,0,sizeof work->media};while(pos<svc->len){if(!next(svc->data,svc->len,&pos,&f))return 0;if(f.number==3){if(f.wire!=2||++count!=1||!layout_media(&media,&f,work)||!message(out,3,&media))return 0;}else if(!put(out,f.raw,f.size))return 0;}return count==1;}
#endif
int cluster_wire_rewrite(const unsigned char *in,unsigned len,unsigned char *out,unsigned capacity,unsigned *outlen){
#if MARGIN_WIDTH_PIXELS || LAYOUT_DENSITY_DPI != 160 || LAYOUT_UI_INSET_PIXELS
 struct LayoutWorkspace *work;Writer result,svc;Field f;unsigned pos=2,base_len=0,found=0;uint64_t id;int ok=0;uintptr_t a=(uintptr_t)in,b=(uintptr_t)out;if(!outlen)return 0;*outlen=0;if(!in||!out||len<2||len>8192||capacity>16384||(b>=a&&b-a<len)||(a>=b&&a-b<capacity))return 0;work=malloc(sizeof(*work));if(!work)return 0;result.p=out;result.n=0;result.cap=capacity;svc.p=work->service;svc.n=0;svc.cap=sizeof work->service;if(!layout_metadata_rewrite(in,len,work->baseline,sizeof work->baseline,&base_len)||!put(&result,work->baseline,2))goto done;while(pos<base_len){if(!next(work->baseline,base_len,&pos,&f))goto done;if(f.number==1){if(f.wire!=2||!service_id(&f,&id))goto done;if(id==9){if(++found!=1||!layout_service(&svc,&f,work)||!message(&result,1,&svc))goto done;continue;}}if(!put(&result,f.raw,f.size))goto done;}if(found!=1)goto done;*outlen=result.n;ok=1;done:free(work);return ok;
#else
 return layout_metadata_rewrite(in,len,out,capacity,outlen);
#endif
}

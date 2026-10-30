#include "wire.h"
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    const unsigned char *raw, *data;
    unsigned size, len, number, wire;
    uint64_t value;
} Field;
typedef struct { unsigned char *p; unsigned n, cap; } Writer;
typedef struct { unsigned char service[16384], descriptor[8192]; } Workspace;

static int var(const unsigned char *p, unsigned n, unsigned *pos, uint64_t *v)
{
    unsigned i; uint64_t x=0;
    for(i=0;i<10;i++) {
        unsigned b;
        if(*pos>=n) return 0;
        b=p[(*pos)++];
        if(i==9 && b>1) return 0;
        x|=(uint64_t)(b&127)<<(7*i);
        if(!(b&128)) { *v=x; return 1; }
    }
    return 0;
}
static int next(const unsigned char *p, unsigned n, unsigned *pos, Field *f)
{
    unsigned start=*pos, d; uint64_t tag, length;
    if(!var(p,n,pos,&tag) || (tag>>3)==0 || (tag>>3)>0x1fffffff) return 0;
    f->number=(unsigned)(tag>>3); f->wire=(unsigned)(tag&7);
    f->value=0; f->data=p+*pos; f->len=0;
    if(f->wire==0) { if(!var(p,n,pos,&f->value)) return 0; }
    else if(f->wire==2) {
        if(!var(p,n,pos,&length) || length>n-*pos) return 0;
        f->data=p+*pos; f->len=(unsigned)length; *pos+=f->len;
    } else if(f->wire==1 || f->wire==5) {
        d=f->wire==1?8:4;
        if(d>n-*pos) return 0;
        f->len=d; *pos+=d;
    } else return 0;
    f->raw=p+start; f->size=*pos-start; return 1;
}
static int put(Writer *w, const unsigned char *p, unsigned n)
{
    if(n>w->cap-w->n) return 0;
    memcpy(w->p+w->n,p,n); w->n+=n; return 1;
}
static int putvar(Writer *w, uint64_t v)
{
    unsigned char b[10]; unsigned n=0;
    do { b[n++]=(unsigned char)((v&127)|(v>127?128:0)); v>>=7; } while(v);
    return put(w,b,n);
}
static int message(Writer *w, unsigned number, const Writer *child)
{
    return putvar(w,((uint64_t)number<<3)|2) && putvar(w,child->n)
        && put(w,child->p,child->n);
}
/* Validate every direct field even when the enclosing service is preserved. */
static int service_id(const Field *service, uint64_t *id)
{
    unsigned pos=0, count=0; Field f;
    while(pos<service->len) {
        if(!next(service->data,service->len,&pos,&f)) return 0;
        if(f.number==1) {
            if(f.wire!=0 || ++count!=1) return 0;
            *id=f.value;
        }
    }
    return count==1;
}
static int descriptor(Writer *out, const Field *desc, unsigned kind, unsigned display)
{
    unsigned pos=0; Field f;
    while(pos<desc->len) {
        if(!next(desc->data,desc->len,&pos,&f)) return 0;
        if((kind==3 && (f.number==6 || f.number==7)) ||
           (kind==4 && f.number==5)) {
            if(f.wire!=0) return 0;
        } else if(!put(out,f.raw,f.size)) return 0;
    }
    if(kind==3)
        return putvar(out,48) && putvar(out,display) && putvar(out,56) && putvar(out,display);
    return putvar(out,40) && putvar(out,display);
}
static int rewrite_service(Writer *out, const Field *s, unsigned kind, unsigned display, Workspace *work)
{
    unsigned pos=0, count=0; Field f;
    Writer child={work->descriptor,0,sizeof work->descriptor};
    while(pos<s->len) {
        if(!next(s->data,s->len,&pos,&f)) return 0;
        if(f.number==kind) {
            if(f.wire!=2 || ++count!=1 || !descriptor(&child,&f,kind,display)
               || !message(out,kind,&child)) return 0;
        } else if(!put(out,f.raw,f.size)) return 0;
    }
    return count==1;
}
static int rewrite(const unsigned char *in, unsigned len,
                        unsigned char *out, unsigned capacity, unsigned *outlen, Workspace *work)
{
    unsigned char ids[32]={0}; uint64_t id=0; unsigned pos=2, seen=0;
    Field f; Writer result={out,0,capacity};
    Writer child={work->service,0,sizeof work->service};
    uintptr_t a=(uintptr_t)in, b=(uintptr_t)out;
    if(!outlen) return 0;
    *outlen=0;
    if(!in || !out || len<2 || len>8192 || capacity>16384 ||
       in[0]!=0 || in[1]!=6) return 0;
    if((b>=a && b-a<len) || (a>=b && a-b<capacity)) return 0;
    if(!put(&result,in,2)) return 0;
    while(pos<len) {
        if(!next(in,len,&pos,&f)) return 0;
        if(f.number!=1) { if(!put(&result,f.raw,f.size)) return 0; continue; }
        if(f.wire!=2 || !service_id(&f,&id)) return 0;
        if(id==0 || id>=255 || (ids[id>>3] & (1u<<(id&7)))) return 0;
        ids[id>>3] |= (unsigned char)(1u<<(id&7));
        if(id==1 || id==2 || id==9 || id==10) {
            child.n=0;
            if(!rewrite_service(&child,&f,(id==1 || id==9)?3:4,id>=9?1:0,work) ||
               !message(&result,1,&child)) return 0;
            seen |= id==1?1u:id==2?2u:id==9?4u:8u;
        } else if(!put(&result,f.raw,f.size)) return 0;
    }
    if(seen!=15) return 0;
    *outlen=result.n; return 1;
}

int cluster_wire_rewrite(const unsigned char *in, unsigned len,
                        unsigned char *out, unsigned capacity, unsigned *outlen)
{
    Workspace *work;
    int ok;
    if(!outlen) return 0;
    *outlen=0;
    if(!in || !out || len<2 || len>8192 || capacity>16384) return 0;
    work=(Workspace *)malloc(sizeof *work);
    if(!work) return 0;
    ok=rewrite(in,len,out,capacity,outlen,work);
    free(work);
    return ok;
}
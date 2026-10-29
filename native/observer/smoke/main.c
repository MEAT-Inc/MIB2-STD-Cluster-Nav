#define _QNX_SOURCE 1
#include "observer.h"
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
extern uint32_t registration(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(OBS_SYMBOL);
extern unsigned smoke_native_calls(void);
int main(int argc,char **argv) {
    unsigned i;
    int observed=argc==2 && !strcmp(argv[1],"observed");
    const struct obs_file *(*view)(void)=0;
    void *symbol=dlsym(RTLD_DEFAULT,"delphi_observer_view");
    if (argc==2 && !strcmp(argv[1],"timeout-control")) { for (;;) pause(); }
    if (argc!=2 || (!observed && strcmp(argv[1],"baseline"))) return 2;
    if (sizeof(view)!=sizeof(symbol)) return 3;
    memcpy(&view,&symbol,sizeof(view));
    if ((view!=0)!=observed) return 4;
    for (i=0;i<9;++i) {
        uintptr_t a=0x1000u+i,b=0x2000u+i;
        uint32_t expected=(uint32_t)(a^b)^0x80000001u,actual;
        errno=ERANGE;
        actual=registration(a,b,0x12345678u,0x87654321u,0x55aa55aau,0xaa55aa55u);
        if (actual!=expected || errno!=EDOM) return 5;
    }
    if (smoke_native_calls()!=9) return 6;
    if (view) {
        const struct obs_file *file=view();
        if (file->header.magic!=OBS_MAGIC || file->header.status!=OBS_READY ||
            file->header.pointer_bytes!=4 || file->header.count!=9 || file->header.dropped) return 7;
        for (i=0;i<9;++i) {
            const struct obs_record *r=&file->records[i];
            if (r->sequence!=i+1 || r->committed!=i+1 || r->thread_sequence!=i+1 ||
                r->receiver!=0x1000u+i || r->endpoint!=0x2000u+i || !r->caller || !r->thread) return 8;
        }
    }
    printf("DELPHI_SMOKE_PASS mode=%s calls=9 registers_stack_errno_return=pass records=%u\n",
        observed?"observed":"baseline",observed?9:0);
    return 0;
}

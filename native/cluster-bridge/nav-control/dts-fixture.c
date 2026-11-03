/* Fixture-only DTS adapter. No unit logger/shared-memory/config changes. */
#include <stdint.h>
#include <stdarg.h>
static int disabled(unsigned component,unsigned level){(void)component;(void)level;return 0;}
static void discard(unsigned component,unsigned level,const char *source,const char *format,...){(void)component;(void)level;(void)source;(void)format;}
void *DTS_Client_Get_Frontend(void){static uintptr_t table[12];table[7]=(uintptr_t)disabled;table[11]=(uintptr_t)discard;return table;}
void DTS_Client_Set_Dt_Level(unsigned a,unsigned b){(void)a;(void)b;}

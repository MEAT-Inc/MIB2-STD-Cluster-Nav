/* Fixture-only DTS adapter. No unit logger/shared-memory/config changes. */
#include <stdint.h>
#include <stdarg.h>
static int disabled(unsigned component,unsigned level){(void)component;(void)level;return 0;}
static void discard(unsigned component,unsigned level,const char *source,const char *format,...){(void)component;(void)level;(void)source;(void)format;}
static void set_level(unsigned a,unsigned b,unsigned c){(void)a;(void)b;(void)c;}
void *DTS_Client_Get_Frontend(void){static uintptr_t table[12];table[7]=(uintptr_t)disabled;table[8]=(uintptr_t)set_level;table[11]=(uintptr_t)discard;return table;}
void DTS_Client_Set_Dt_Level(unsigned a,unsigned b){(void)a;(void)b;}

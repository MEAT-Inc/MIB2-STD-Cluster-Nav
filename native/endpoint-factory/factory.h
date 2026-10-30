#ifndef DELPHI_FACTORY_H
#define DELPHI_FACTORY_H
#include <stdint.h>
struct factory_shared { uint32_t *count; void *object; };
struct factory_result { uint32_t error,video_constructed,input_constructed,callback_wrapped,callback_attached,temp_released,configurations,input_destroyed,video_destroyed,callback_destroyed,unexpected_callback,quarantined; };
struct factory_api {
 void *(*allocate)(unsigned); void (*deallocate)(void*);
 void (*video_ctor)(void*,unsigned char,void*,unsigned char);
 void (*input_ctor)(void*,unsigned char,void*);
 void (*wrap)(struct factory_shared*,void*);
 void (*attach)(void*,const struct factory_shared*);
 void (*release)(struct factory_shared*);
 void (*video_delete)(void*); void (*input_delete)(void*);
 int (*add_config)(void*,int,int,int,int,int,int,int);
 unsigned (*config_count)(void*);
 uintptr_t video_vptr,input_vptr;
};
/* Isolated construction only. No registration, discovery, focus or media calls. */
int factory_run(const struct factory_api*,void*,struct factory_result*);
#endif

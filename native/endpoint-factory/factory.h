#ifndef DELPHI_FACTORY_H
#define DELPHI_FACTORY_H
#include <stdint.h>
struct factory_shared { uint32_t *count; void *object; };
struct factory_result { uint32_t error,video_constructed,input_constructed,callback_wrapped,callback_attached,temp_released,configurations,input_destroyed,video_destroyed,callback_destroyed,unexpected_callback,quarantined,codec_calls,start_calls,stop_calls,media_config_calls,focus_calls,data_calls,data_bytes; };
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
 int (*media_start)(void*,const void*); int (*media_stop)(void*,const void*);
 int (*codec)(void*,void*,unsigned);
 int (*data)(void*,uint64_t,const struct factory_shared*,unsigned);
 int (*focus_request)(void*,const void*);
 void (*input_key)(void*,void*,const int*);
 uintptr_t video_vptr,input_vptr;
};
/* Isolated construction only. No registration, discovery or outgoing packets. */
int factory_trigger(unsigned,uintptr_t,volatile uint32_t*);
int factory_run(const struct factory_api*,void*,struct factory_result*);
#endif

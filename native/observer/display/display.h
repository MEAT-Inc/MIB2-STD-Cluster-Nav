#ifndef DELPHI_DISPLAY_H
#define DELPHI_DISPLAY_H
#include "../observer.h"
#define DISPLAY_MAGIC 0x32434c44u
#define DISPLAY_CAPACITY 32u
#define DISPLAY_PAYLOAD 4096u
#define CONFIG_SYMBOL "_ZN9VideoSink25addSupportedConfigurationEiiiiiii"
#define FOCUS_SYMBOL "_ZN9VideoSink13setVideoFocusEib"
#define QUEUE_SYMBOL "_ZN13MessageRouter13queueOutgoingEhPvj"
struct display_record {
 uint32_t sequence,event,thread,argc,caller,args[8],payload_bytes,flags,committed;
 unsigned char payload[DISPLAY_PAYLOAD];
};
struct display_file {struct obs_header header;struct display_record records[DISPLAY_CAPACITY];};
#endif

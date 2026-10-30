#ifndef DELPHI_LAUNCH_H
#define DELPHI_LAUNCH_H
#include <stdint.h>
#define LAUNCH_MAGIC 0x314c4144u
#define LAUNCH_PREFIX "/ramdisk/delphi-aa-observer_"
#define LAUNCH_ACTIVE "/dev/shmem/delphi-aa-observer-active.bin"
#define AA_TARGET "/extbin/apps/bin/AndroidAuto"
#define RECEIVER_TARGET "/extbin/apps/lib/libautoreceiver.so.1"
#define MANAGER_TARGET "/proc/boot/procman"
struct launch_state {
 uint32_t magic,version,bytes;
 volatile uint32_t phase,error,guard_armed,alias_removed,initial_signal_error;
 volatile uint32_t observed_signal_error,restoration_verified,observed_pid,restored_pid;
 uint32_t controller_pid,manager_pid,baseline_pid;
 volatile uint32_t guard_done;
 uint64_t baseline_start,manager_start;
 volatile uint64_t observed_start,restored_start;
 char root[128];
 uint32_t obs_status,obs_count,obs_dropped,binding_slot,binding_value,expected_binding,got_valid,observer_base;
 uint32_t capture_seconds;
 volatile uint32_t capture_done,cleanup_authorized,cleanup_started;
 uint32_t reserved[60];
};
#endif

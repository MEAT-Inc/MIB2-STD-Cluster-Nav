#ifndef DELPHI_NAV_LAUNCH_H
#define DELPHI_NAV_LAUNCH_H
#include <stdint.h>
#define LAUNCH_MAGIC 0x314e4c44u
#define LAUNCH_PREFIX "/ramdisk/delphi-nav-bridge_"
#define LAUNCH_ACTIVE "/dev/shmem/delphi-nav-launch-active.bin"
#define NAV_TARGET "/extbin/apps/bin/NavigationServer"
#define NAV_CONFIG "/extbin/apps/cfg/NAV/v0/NC/Delphi/NavServer.cfg"
#define NAV_CONFIG_REL "../cfg/NAV/v0/NC/Delphi/NavServer.cfg"
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
 char inherited_cwd[128];
 uint32_t reserved[28];
};
#endif

#ifndef TX_BENCH_H
#define TX_BENCH_H
#define TX_TARGET "/proc/boot/tx_stock"
#define TX_COPY "/proc/boot/tx_original"
#define TX_WRAPPER "/proc/boot/tx_control"
#define TX_REPORT "/dev/shmem/delphi-launch-bench-report"
struct tx_report {
 volatile unsigned armed,done,watchdog_finished,watchdog_removed;
 volatile unsigned app_runs,observed_runs,last_pid,last_ppid,arguments_ok;
};
#endif

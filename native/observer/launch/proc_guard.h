#ifndef PROC_GUARD_H
#define PROC_GUARD_H
#include <sys/types.h>
#include <stdint.h>
#include <stddef.h>
typedef struct pg_identity {
    pid_t pid, parent;
    uint64_t start_time;
    char executable[1024];
    uint64_t base_address;
} pg_identity;
/* Success: held fd for open/find; 0 for read/matches/interrupt. Failure: -1,
 * errno set. Caller closes returned descriptors. pg_interrupt rechecks a held descriptor, then uses kill(SIGINT); not atomic. */
int pg_open(pid_t pid, int writable, pg_identity *out);
int pg_read_identity(int fd, pg_identity *out);
int pg_matches(int fd, const pg_identity *expected);
int pg_interrupt(int fd, const pg_identity *expected);
int pg_find(const char *exactpath, pid_t parent, pg_identity *out);
#endif

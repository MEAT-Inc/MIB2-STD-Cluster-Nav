#ifndef CLUSTER_WIRE_H
#define CLUSTER_WIRE_H
/* Input is a complete 00 06 discovery response, at most 8192 bytes.
 * Output capacity must be at most 16384. Buffers must not overlap.
 * Returns 1 on success, 0 on rejection; *outlen is zero on rejection.
 * Output may contain partial bytes on rejection. Input is never modified.
 */
int cluster_wire_rewrite(const unsigned char *in, unsigned len,
                        unsigned char *out, unsigned capacity, unsigned *outlen);
#endif

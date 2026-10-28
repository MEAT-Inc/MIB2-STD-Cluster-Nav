Delphi registration observer v1 - compiled production candidate

Purpose
Entry-only observation of existing registerService calls on the acquired Delphi
MIB2 Standard build. Does not create services, inspect endpoint objects, modify
phone discovery, request video, or change native navigation/cluster transport.
Records every intercepted caller, including raw caller LR, opaque receiver and
endpoint words, PID/thread ID and accepted-record global/per-thread sequences.
Known link-time caller LR for this sample is 0x124e54. Interpret runtime addresses
only after verifying the main application's load bias; no address is patched.

Why entry-only
The ARM shim restores arguments and SP/LR, then bx's to the original function.
There is no observer frame during native execution. Return registers, native
exceptions and nonlocal exits go directly to the original caller. No guessed
C++ return type, ownership layout, stdlib ABI or exception personality is used.
This deliberately replaces the earlier enter/leave design. It does not log native
return values, completion, or duration. Absence of completion cannot be inferred.
The temporary logger frame is .cantunwind; asynchronous unwinding through that
short frame is not supported. The observer is for ordinary application threads.

Logging and synchronization
1024 fixed 32-byte records plus a 128-byte versioned header. A single nonwaiting
try-lock guards appending and logger reentry. Contended or full logs drop metadata
and still forward the original exactly once. No heap allocation, file I/O,
formatting or loader calls occur on the normal capture path. getpid, pthread_self
and errno access remain; all observer imports bind eagerly (-z now). Argument
pointees are never accessed and references are not acquired/released.
Records contain pointer identities as integers only; they do not retain objects.
The mapping is initialized/prefaulted in the constructor, but this is not a
hard-realtime or zero-overhead guarantee. Timing must be compared on the car.
Drop count saturates at uint32 max. Accounting makes at most four CAS attempts;
if contended further, drop_flags marks the count as a lower bound. Per-thread
sequence storage tracks 64 thread IDs; additional IDs are flagged untracked.
Sequences count accepted log records, not all native calls. Thread IDs may be
reused by the OS. Forked children forward but do not modify the parent's log.

Log object
QNX default: /dev/shmem/delphi-observer-<pid>.bin, mode 0600, exclusive creation.
Optional DELPHI_OBSERVER_LOG must begin /dev/shmem/delphi-observer- and contain
only a single safe filename suffix. Existing files are never overwritten.
Invalid paths, open/truncate/mmap failures disable logging while retaining native
forwarding. Exported delphi_observer_view reports resolved/log-disabled status.
No destructor races with active threads; OS process teardown releases mappings.
Logs remain in RAM until explicitly collected/removed or the unit restarts.
Collected raw CAR captures belong in delphi-dump/observer/ in the laptop workspace.
Decode a copied log with:
  python scripts/decode_delphi_observer.py <capture.bin> --output <capture.json>
A live copy can be inconsistent: the decoder rejects uncommitted records and
invalid bounds. For a final capture, stop its diagnostic process before copying.

Original resolution and failure policy
Constructor resolves RTLD_NEXT, verifies dladdr ownership is outside this DSO and
has basename libautoreceiver.so or libautoreceiver.so.1. The native pointer and
module base are recorded. These are identity clues, not runtime SHA verification.
If the original is missing or belongs to a different module, startup is refused
with exit 125 and a fixed stderr message. There is no fabricated return, null
branch or attempted retry. Calls before constructor resolution also refuse;
constructor completion before application calls is a deployment precondition.
Logging failures alone NEVER cause that refusal. Do not preload this library
into an unrelated process. Do not globally export LD_PRELOAD.

Validation and readiness
Host and emulated QNX tests cover 8-thread contention/full buffers, native call
counts and high return bits, errno, C++ exception propagation, siglongjmp,
recursive native calls, fork forwarding, disabled logging, existing log content,
missing/wrong native modules, repeated starts and ARM register/VFP/stack ABI.
The QNX fixture's C++ runtime is synthetic GCC; it is not the vendor runtime.
Only libc.so.3 is needed by the observer. The release contains NO fixture,
replacement receiver library, C++ runtime, acquired firmware or installer.
The packager checks exact acquired AndroidAuto/libautoreceiver hashes, dynamic
relocations, export surface, nonexecutable stack, eager binding, tail assembly
and a test-log/binary hash match. This checks local samples, not live target files.

Release files
libdelphi_observer.so, manifest.json, decode_delphi_observer.py, README.txt.
Rebuild/test/package from project root (Docker images already prepared):
  .\scripts\test_delphi_observer.ps1

This candidate is NOT vehicle validated or approved for unattended deployment.
Before a vehicle run: verify the live executable/receiver hashes against manifest,
confirm the actual supervised launch arguments/environment and process maps,
prepare a verified stock restart path, then launch one diagnostic child with
process-scoped preload. No vehicle upload/restart or startup edit was performed.
No new map endpoint or Android Auto display is enabled by this library.

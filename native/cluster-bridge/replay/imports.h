#ifndef DELPHI_REPLAY_IMPORTS_H
#define DELPHI_REPLAY_IMPORTS_H
#include <stdint.h>
/* Caller verifies image identity and writable PT_LOAD ownership before calling.
 * Slot order for the pinned NavigationServer: open, write, close. */
#define REPLAY_IMPORT_OPEN_SLOT 0x5a77e8u
#define REPLAY_IMPORT_WRITE_SLOT 0x5a7554u
#define REPLAY_IMPORT_CLOSE_SLOT 0x5a78acu
#define REPLAY_IMPORT_LAZY 0x122418u
#define REPLAY_IMPORT_RW_BEGIN 0x5a50c4u
#define REPLAY_IMPORT_RW_END 0x5ac940u
struct replay_import {
 volatile uint32_t *slot;
 uint32_t native,lazy,replacement,saved;
};
/* 0 success; -1 refused with own stores rolled back; -2 rollback incomplete.
 * No stores occur unless all three descriptors and initial values validate.
 * Never overwrite a value another writer has installed. */
int replay_imports_install(struct replay_import *,unsigned);
int replay_imports_restore(struct replay_import *,unsigned);
#endif

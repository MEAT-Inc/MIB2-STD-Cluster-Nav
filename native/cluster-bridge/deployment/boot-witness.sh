#!/bin/sh
# Fixed-size receipt only, once per kernel boot. No media/process manipulation.
case "$1" in
  *[!0-9a-f]*|"") exit 0 ;;
esac
[ "${#1}" -eq 32 ] || exit 0
case "$SYSTEM_RUNMODE" in ""|normal) ;; *) exit 0 ;; esac
root=/persistence/delphi-cluster-launcher-v1
umask 022
# /ramdisk is reset by a full boot. Duplicate HMI launches cannot grow logs.
mkdir /ramdisk/delphi-startup-witness-v1 2>/dev/null || exit 0
{
  printf 'BOOT_WITNESS_V1\ninstallation=%s\n' "$1"
  printf 'launch_pid=%s\nparent_pid=%s\n' "$$" "$PPID"
  printf 'runmode=%s\n' "${SYSTEM_RUNMODE:-unset}"
} > "$root/receipt.tmp" || exit 0
mv -f "$root/receipt.tmp" "$root/receipt.txt"
exit 0

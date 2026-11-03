#!/bin/sh
# Shared UI for the container build/test scripts. Source, then console_start.
console_status() {
    console_level=$1
    shift
    console_color=96
    case "$console_level" in STEP) console_color=94 ;; OK) console_color=92 ;; ERROR) console_color=91 ;; esac
    if [ -t 2 ] && [ "${NO_COLOR+x}" != x ] && [ "${TERM:-}" != dumb ]; then
        printf '\033[%sm[%s] [%-6s]\033[0m %s\n' "$console_color" "$(date +%H:%M:%S)" "$console_level" "$*" >&2
    else
        printf '[%s] [%-6s] %s\n' "$(date +%H:%M:%S)" "$console_level" "$*" >&2
    fi
}

console_finish() {
    console_code=$1
    if [ "$console_code" -eq 0 ]; then
        console_status OK "Finished $0 (exit 0)."
    else
        console_status ERROR "Stopped $0 (exit $console_code)."
    fi
}

console_start() {
    console_use_case=$1
    shift
    if [ -z "${PROJECT_CONSOLE_DEPTH:-}" ] && [ -t 2 ]; then
        printf '\033[2J\033[H' >&2
    fi
    PROJECT_CONSOLE_DEPTH=1
    export PROJECT_CONSOLE_DEPTH
    printf '\n========================================================================\n' >&2
    printf '%s | version %s\n' "${0##*/}" "${SCRIPT_VERSION:-1.0}" >&2
    printf 'Arguments:' >&2
    if [ "$#" -eq 0 ]; then printf ' (none)' >&2; else printf ' <%s>' "$@" >&2; fi
    printf '\nUse case: %s\n' "$console_use_case" >&2
    printf '========================================================================\n' >&2
    console_status STEP 'Starting script.'
    trap 'console_finish $?' 0
}

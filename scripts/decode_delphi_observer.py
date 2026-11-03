"""Decode a copied Delphi observer log without executing any target code."""
from project_console import console_session, log as print
from pathlib import Path
import argparse, json, struct
HEADER = struct.Struct('<32I')
RECORD = struct.Struct('<8I')
MAGIC = 0x314f4c44

def decode(data):
    if len(data) < HEADER.size:
        raise ValueError('Truncated header')
    h = HEADER.unpack_from(data)
    if h[0] != MAGIC or h[1] != 1 or h[2] != 128 or h[3] != 32 or h[4] != 1024:
        raise ValueError('Unsupported observer format')
    if h[5] not in (4, 8) or h[9] not in (1, 3) or h[10] > h[4]:
        raise ValueError('Invalid header values')
    if len(data) != h[2] + h[3] * h[4]:
        raise ValueError('Incorrect log length')
    records, incomplete = [], []
    last_by_thread = {}
    for i in range(h[10]):
        r = RECORD.unpack_from(data, h[2] + i * h[3])
        if r[0] != i+1 or r[7] != i+1:
            incomplete.append(i+1)
            continue
        if r[6] & ~1:
            raise ValueError('Unknown record flags')
        if not r[6] & 1:
            if not r[2] or r[2] <= last_by_thread.get(r[1], 0):
                raise ValueError('Non-increasing sequence for thread ID')
            last_by_thread[r[1]] = r[2]
        records.append(dict(sequence=r[0], thread=r[1], thread_sequence=r[2],
            receiver=f'0x{r[3]:08x}', endpoint=f'0x{r[4]:08x}', caller=f'0x{r[5]:08x}', flags=r[6]))
    return dict(format_version=1, pointer_bytes=h[5], pid=h[6], native_address=f'0x{h[7]:08x}',
        module_base=f'0x{h[8]:08x}', logging_disabled=bool(h[9]&2), count=h[10],
        dropped=h[11], dropped_is_lower_bound=bool(h[12]), writer_active=bool(h[13]),
        incomplete_records=incomplete, events='entry_only', records=records)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = decode(args.log.read_bytes())
    encoded = json.dumps(result, indent=2)
    if args.output: args.output.write_text(encoded, encoding='utf-8')
    else: print(encoded)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()

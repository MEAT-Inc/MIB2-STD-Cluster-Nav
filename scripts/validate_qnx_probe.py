"""Static acceptance gate for synthetic QNX probe artifacts, never executes them."""
from project_console import console_session, log as print
from pathlib import Path
import hashlib, json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from elftools.elf.elffile import ELFFile
SYMBOL = '_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase'
OUT = ROOT / 'native/loader-probe/build-qnx'

def inspect(path):
    with path.open('rb') as f:
        elf = ELFFile(f)
        assert elf.elfclass == 32 and elf.little_endian
        assert elf['e_machine'] == 'EM_ARM'
        flags = elf['e_flags']
        assert flags >> 24 == 5, 'Expected ARM EABI5'
        assert not flags & 0x400, 'Unexpected hard-float PCS'
        needed, interpreter, relocations, imports, exports = [], None, [], [], []
        for seg in elf.iter_segments():
            if seg['p_type'] == 'PT_INTERP': interpreter = seg.get_interp_name()
            if seg['p_type'] == 'PT_DYNAMIC':
                needed += [t.needed for t in seg.iter_tags() if t.entry.d_tag == 'DT_NEEDED']
        for section in elf.iter_sections():
            if section['sh_type'] in ('SHT_REL', 'SHT_RELA'):
                symbols = elf.get_section(section['sh_link'])
                for reloc in section.iter_relocations():
                    name = symbols.get_symbol(reloc['r_info_sym']).name if reloc['r_info_sym'] else ''
                    relocations.append({'type': reloc['r_info_type'], 'symbol': name})
            if section['sh_type'] == 'SHT_DYNSYM':
                for symbol in section.iter_symbols():
                    if symbol.name:
                        (imports if symbol['st_shndx'] == 'SHN_UNDEF' else exports).append(symbol.name)
        assert set(needed) <= {'libc.so.3', 'libprobe_provider.so', 'libprobe_observer.so'}, needed
        # Known QNX ARM loader relocation subset; reject unfamiliar emitted kinds.
        assert all(r['type'] in {2, 20, 21, 22, 23} for r in relocations), relocations
        is_library = path.name.endswith('.so')
        assert elf['e_type'] == ('ET_DYN' if is_library else 'ET_EXEC')
        assert interpreter == (None if is_library else '/usr/lib/ldqnx.so.2'), interpreter
        if path.name == 'probe_main':
            assert SYMBOL in imports
            assert any(r['type'] == 22 and r['symbol'] == SYMBOL for r in relocations)
        if path.name in {'libprobe_provider.so', 'libprobe_observer.so'}:
            assert SYMBOL in exports
        return {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'flags': hex(flags), 'needed': needed, 'interpreter': interpreter,
                'imports': imports, 'exports': exports, 'relocations': relocations}

def main():
    results = [inspect(OUT / name) for name in ('probe_main', 'probe_runner', 'probe_linked', 'libprobe_provider.so', 'libprobe_observer.so')]
    report = {'static_checks': 'PASS', 'vehicle_validated': False, 'artifacts': results}
    (OUT / 'elf-validation.json').write_text(json.dumps(report, indent=2))
    print('PASS: five ARM32 LE EABI5 artifacts; soft-float PCS; expected loader/dependencies/relocations.')
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()

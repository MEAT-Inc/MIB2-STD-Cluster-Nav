"""Offline release gate. Proprietary vehicle binaries are read, never packaged."""
from project_console import console_session, log as print
from pathlib import Path
import hashlib, json, shutil, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
SYMBOL = '_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase'
TARGETS = {
 'AndroidAuto': ('extbin/apps/bin/AndroidAuto', 'da1fd5776f6b85962b84ad77c6f564d3f09dd8079652229cda57b4138060c271'),
 'libautoreceiver.so': ('extbin/apps/lib/libautoreceiver.so', 'e14aa58d7867955d968d291fd43b941223fb5072ca7184d8885ef40f2323c92d')}
BUILD = ROOT / 'native/observer/build-qnx'
LIB = BUILD / 'libdelphi_observer.so'

def require(ok, message):
    if not ok: raise RuntimeError(message)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def validate():
    for name, (path, expected) in TARGETS.items():
        require(sha(ROOT / 'delphi-dump' / path) == expected, 'Target sample changed: ' + name)
    with LIB.open('rb') as stream:
        elf = ELFFile(stream)
        require(elf.elfclass == 32 and elf.little_endian and elf['e_machine'] == 'EM_ARM' and elf['e_type'] == 'ET_DYN', 'Wrong ELF architecture/type')
        require(elf['e_flags'] >> 24 == 5 and not elf['e_flags'] & 0x400, 'Wrong ARM EABI/PCS')
        needed, imports, exports, relocations = [], [], [], []
        eager_binding = False
        for seg in elf.iter_segments():
            if seg['p_type'] == 'PT_GNU_STACK': require(not seg['p_flags'] & 1, 'Executable stack')
            if seg['p_type'] == 'PT_DYNAMIC':
                for tag in seg.iter_tags():
                    if tag.entry.d_tag == 'DT_NEEDED': needed.append(tag.needed)
                    if tag.entry.d_tag == 'DT_BIND_NOW': eager_binding = True
                    if tag.entry.d_tag == 'DT_FLAGS' and tag.entry.d_val & 8: eager_binding = True
                    require(tag.entry.d_tag != 'DT_TEXTREL', 'Text relocations')
        require(eager_binding, 'Critical-path imports must bind eagerly')
        require(needed == ['libc.so.3'], 'Observer must depend only on libc: ' + repr(needed))
        symtab = elf.get_section_by_name('.symtab')
        for section in elf.iter_sections():
            if section['sh_type'] == 'SHT_DYNSYM':
                for symbol in section.iter_symbols():
                    if symbol.name:
                        (imports if symbol['st_shndx'] == 'SHN_UNDEF' else exports).append(symbol.name)
            if section['sh_type'] in ('SHT_REL', 'SHT_RELA') and section['sh_flags'] & 2:
                relocations += [r['r_info_type'] for r in section.iter_relocations()]
        require(set(exports) == {SYMBOL, 'delphi_observer_view'}, 'Unexpected exports: ' + repr(exports))
        require(all(r in {2,20,21,22,23} for r in relocations), 'Unsupported dynamic relocation')
        require(not any(n.startswith(('__atomic_', '__sync_')) for n in imports), 'External atomic runtime')
        require(not any(n.startswith(('_Unwind_', '__cxa_throw')) for n in imports), 'Unexpected observer C++ unwind runtime')
        symbol = symtab.get_symbol_by_name(SYMBOL)[0]
        section = elf.get_section(symbol['st_shndx'])
        offset = symbol['st_value'] - section['sh_addr']
        body = section.data()[offset:offset+symbol['st_size']]
        asm = list(Cs(CS_ARCH_ARM, CS_MODE_ARM).disasm(body, symbol['st_value']))
        require([i.mnemonic for i in asm] == ['push','vpush','ldr','bl','str','vpop','pop','bx'], 'Tail-wrapper control flow changed')
        require(asm[2].op_str == 'r2, [sp, #0x54]' and asm[4].op_str == 'r0, [sp, #0x50]' and asm[-1].op_str == 'ip', 'Saved-LR / tail-target offsets changed')
        assembly = '\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in asm)
    log = BUILD / 'qemu/qemu.log'
    require((BUILD / 'qemu/observer-tested.sha256').read_text().split()[0] == sha(LIB), 'Library differs from tested artifact')
    raw = log.read_text(errors='replace')
    require('OBSERVER_QNX_SUITE_PASS' in raw and 'OBSERVER_ARM_ABI_PASS' in raw, 'QNX native tests did not pass')
    require('terminated SIG' not in raw, 'Guest fatal signal')
    return dict(artifact='libdelphi_observer.so', sha256=sha(LIB), abi='ARM32 LE EABI5 base PCS',
        toolchain_revision='baa45224f18ae6b13c2e9c77c6663bb8181eb6a1',
        target_train='MST2_US_VW_P0890D',
        expected_target_sha256={n:e for n,(p,e) in TARGETS.items()},
        event_mode='entry_only_tail_call', exports=exports, imports=imports,
        needed=needed, dynamic_relocations=relocations, wrapper_assembly=assembly,
        qnx_test_log_sha256=sha(log), vehicle_validated=False,
        runtime_fingerprints_verified=False, deployment_ready=False)

def main():
    report = validate()
    release = ROOT / 'native/observer/release'
    release.mkdir(exist_ok=True)
    shutil.copy2(LIB, release / LIB.name)
    shutil.copy2(ROOT / 'scripts/decode_delphi_observer.py', release / 'decode_delphi_observer.py')
    shutil.copy2(ROOT / 'scripts/project_console.py', release / 'project_console.py')
    if (ROOT / 'native/observer/README.txt').exists(): shutil.copy2(ROOT / 'native/observer/README.txt', release / 'README.txt')
    report['files'] = {p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in (release / LIB.name, release / 'decode_delphi_observer.py', release / 'project_console.py', release / 'README.txt')}
    (release / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    with zipfile.ZipFile(release.parent / 'delphi-observer-v1.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('libdelphi_observer.so', 'manifest.json', 'decode_delphi_observer.py', 'project_console.py', 'README.txt'):
            archive.write(release / name, name)
    print('PASS: matched target samples; validated ARM tail wrapper, libc-only dependencies and QNX tests.')
    print('Release candidate:', release)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()

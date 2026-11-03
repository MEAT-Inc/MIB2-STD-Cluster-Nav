"""Reproduce local Java conversion/subset decompilation; no vehicle code is executed."""
from project_console import console_session, log as print
with console_session(__file__, __doc__, enabled=__name__ == '__main__'):
    from pathlib import Path
    import hashlib,json,os,shutil,subprocess,sys,zipfile
    BASE=Path(__file__).resolve().parents[1]; TOOL=BASE/'.tools/display-hmi-jxe2jar'; OUT=BASE/'delphi-analysis/display-hmi-java';OUT.mkdir(exist_ok=True)
    source=BASE/'delphi-analysis/extracted/vwjxe/MIBHMI.jxe';jar=OUT/'MIBHMI.jar'
    if not jar.exists():
     with (OUT/'conversion.log').open('w',encoding='utf-8') as log:subprocess.run([sys.executable,str(TOOL/'src/jxe2jar.py'),str(source),str(jar)],cwd=BASE,stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run([sys.executable,str(BASE/'scripts/display_hmi_subset.py')],cwd=BASE,check=True)
    def jdk_tool(name):
     home=os.environ.get('JAVA_HOME')
     tool=Path(home)/'bin'/(name+('.exe' if os.name=='nt' else '')) if home else shutil.which(name)
     if not tool or not Path(tool).is_file():raise RuntimeError('Install a JDK on PATH or set JAVA_HOME; missing '+name)
     return Path(tool)
    java=jdk_tool('java')
    with (OUT/'decompile.log').open('w',encoding='utf-8') as log:subprocess.run([str(java),'-jar',str(TOOL/'tools/cfr-0.152.jar'),str(OUT/'targeted.jar'),'--outputdir',str(OUT/'decompiled'),'--extraclasspath',str(jar),'--silent','true'],cwd=BASE,stdout=log,stderr=subprocess.STDOUT,check=True)
    javap=jdk_tool('javap')
    classes=['de.vw.mib.asl.internal.androidauto.target.RequestHandler','de.vw.mib.asl.internal.androidauto.target.NavigationListener','de.vw.mib.bap.mqbab2.navsd.functions.InfoStates']
    with (OUT/'phone-navigation-bytecode.txt').open('w',encoding='utf-8') as log:subprocess.run([str(javap),'-classpath',str(jar),'-c','-p',*classes],cwd=BASE,stdout=log,stderr=subprocess.STDOUT,check=True)
    with zipfile.ZipFile(jar) as z:
     entries=[n for n in z.namelist() if n.endswith('.class')];bad_crc=z.testzip();bad_magic=[n for n in entries if z.read(n)[:4]!=b'\xca\xfe\xba\xbe']
    log=(OUT/'conversion.log').read_text(encoding='utf-8',errors='replace')
    prov={'converter':'https://github.com/luka-dev/jxe2jar','converter_commit':subprocess.check_output(['git','-C',str(TOOL),'rev-parse','HEAD'],text=True).strip(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'jar_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'written_classes':len(entries),'bad_crc_entry':bad_crc,'bad_class_magic':bad_magic,'skipped_class_log_lines':[s for s in log.splitlines() if 'bad class, skip' in s],'cfr_sha256':hashlib.sha256((TOOL/'tools/cfr-0.152.jar').read_bytes()).hexdigest(),'validation_limit':'CRC/magic and selected javap parsing only; no complete bytecode verifier or recompilation; no vehicle classes executed','license_note':'No repository root LICENSE found at reviewed converter pin. Local analysis checkout only; do not redistribute converter or proprietary firmware classes as a release.'}
    (OUT/'provenance.json').write_text(json.dumps(prov,indent=2),encoding='utf-8');print(json.dumps(prov,indent=2))

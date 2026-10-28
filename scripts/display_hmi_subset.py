from pathlib import Path
import zipfile
base=Path(__file__).resolve().parents[1];root=base/'delphi-analysis/display-hmi-java';src=root/'MIBHMI.jar';out=root/'targeted.jar'
with zipfile.ZipFile(src) as z,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as w:
 names=[n for n in z.namelist() if n.endswith('.class') and (n.startswith('de/vw/mib/asl/internal/navigation/map/') or n.startswith('de/vw/mib/asl/internal/androidauto/target/') or n.startswith('de/vw/mib/asl/internal/carplay/common/') or 'MapViewer' in n or 'MapIntegration' in n or n.startswith('de/vw/mib/asl/internal/smartphoneintegration/target/') or n.startswith('de/vw/mib/asl/internal/exboxm/api/impl/guidance/') or n.startswith('de/vw/mib/asl/internal/androidauto/api/impl/') or n=='de/vw/mib/bap/mqbab2/navsd/functions/InfoStates.class')]
 for name in names:w.writestr(name,z.read(name))
print('Selected',len(names),'classes')


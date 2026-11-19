"""Offline firmware validation and factory-preserving startup candidate checks."""
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_cluster_startup import ROOT, HOOK, prepare, review

EVIDENCE = ROOT / 'delphi-dump/_deployment_preflight_20261119_131638_794286b0/deployment-preflight'


class StartupReviewTests(unittest.TestCase):
    def test_real_evidence_and_exact_rollback(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'review'
            report = prepare(EVIDENCE, out)
            stock = (EVIDENCE / 'runHMI.sh').read_bytes()
            self.assertEqual((out / 'runHMI.sh.stock').read_bytes(), stock)
            self.assertEqual((out / 'runHMI.sh.candidate').read_bytes(), stock + HOOK)
            self.assertFalse(report['install_ready'])
            self.assertFalse(report['remote_write_performed'])
            with self.assertRaises(FileExistsError):
                prepare(EVIDENCE, out)

    def test_changed_firmware_rejected_even_with_updated_capture_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            evidence = Path(td) / 'evidence'
            shutil.copytree(EVIDENCE, evidence)
            data = (evidence / 'runHMI.sh').read_bytes() + b'\n# change\n'
            (evidence / 'runHMI.sh').write_bytes(data)
            summary = json.loads((evidence / 'preflight-summary.json').read_text())
            summary['files'][0].update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            (evidence / 'preflight-summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, 'Unsupported or changed firmware'):
                prepare(evidence, Path(td) / 'rejected')
            self.assertFalse((Path(td) / 'rejected').exists())

    def test_missing_or_failed_launch_and_mount_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            evidence = Path(td) / 'evidence'
            shutil.copytree(EVIDENCE, evidence)
            for name, replacement in [('procman-arguments.txt', 'procman -f /other.cfg'),
                                      ('mounts.txt', '/dev/other on /extbin type dos')]:
                old = (evidence / name).read_bytes()
                (evidence / name).write_text(replacement)
                with self.subTest(name=name), self.assertRaises(ValueError):
                    review(evidence)
                (evidence / name).write_bytes(old)
            summary = json.loads((evidence / 'preflight-summary.json').read_text())
            summary['commands'][0]['exit_code'] = 1
            (evidence / 'preflight-summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, 'Required preflight command'):
                review(evidence)


if __name__ == '__main__':
    from project_console import console_session
    with console_session(__file__, __doc__):
        unittest.main()

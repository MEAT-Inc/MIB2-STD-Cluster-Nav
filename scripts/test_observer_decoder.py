from project_console import console_session
import struct
import unittest
from pathlib import Path
from decode_delphi_observer import decode
ROOT = Path(__file__).resolve().parents[1]
class DecoderTests(unittest.TestCase):
    def setUp(self):
        self.data = (ROOT / 'native/observer/build-host/host-capture.bin').read_bytes()
    def change(self, offset, value):
        data = bytearray(self.data)
        struct.pack_into('<I', data, offset, value)
        return data
    def test_real_concurrent_capture(self):
        result = decode(self.data)
        self.assertGreaterEqual(result['count'], 24)
        self.assertLessEqual(result['count'], 1024)
        self.assertEqual(len(result['records']), result['count'])
        self.assertEqual(result['events'], 'entry_only')
    def test_truncation(self):
        for length in (0, 127, len(self.data)-1):
            with self.assertRaises(ValueError): decode(self.data[:length])
    def test_wrong_magic(self):
        with self.assertRaises(ValueError): decode(self.change(0, 0))
    def test_unbounded_count_rejected(self):
        with self.assertRaises(ValueError): decode(self.change(40, 0xffffffff))
    def test_incomplete_record_not_reported_as_committed(self):
        result = decode(self.change(128+28, 0))
        self.assertEqual(result['incomplete_records'], [1])
        self.assertEqual(len(result['records']), result['count'] - 1)
    def test_thread_sequence_reversal(self):
        with self.assertRaises(ValueError): decode(self.change(128+32+8, 1))
    def test_dropped_lower_bound_flag(self):
        self.assertTrue(decode(self.change(48, 1))['dropped_is_lower_bound'])
    def test_arm_format(self):
        self.assertEqual(decode(self.change(20, 4))['pointer_bytes'], 4)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()

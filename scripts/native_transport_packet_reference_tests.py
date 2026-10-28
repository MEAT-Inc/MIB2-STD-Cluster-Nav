import unittest
from native_transport_packet_reference import *
class NativePacketReferenceTests(unittest.TestCase):
 def test_independent_fixed_crc_constants_from_binary(self):
  self.assertEqual(crc32_mpeg2(PAT_SECTION[:-4]),0x2d50981b)
  self.assertEqual(crc32_mpeg2(PMT_SECTION[:-4]),0xfee61f98)
  self.assertEqual(crc32_mpeg2(PAT_SECTION),0)
  self.assertEqual(crc32_mpeg2(PMT_SECTION),0)
 def test_native_program_and_distinct_pcr_pid(self):
  result=validate_ts(reference_packet(0,PAT_SECTION)+reference_packet(0x10,PMT_SECTION))
  self.assertEqual(result['pat']['programs'],{1:0x10})
  pmt=result['pmts'][0x10]
  self.assertEqual(pmt['program_number'],1)
  self.assertEqual(pmt['pcr_pid'],0x1000)
  self.assertEqual(pmt['streams'],[{'stream_type':0x1b,'pid':0x11,'descriptors':'2a077fff000005dddf28044280323f'}])
 def test_crc_corruption_rejected(self):
  data=bytearray(reference_packet(0,PAT_SECTION));data[15]^=1
  with self.assertRaisesRegex(ValueError,'CRC'):validate_ts(bytes(data))
 def test_wrong_stride_rejected(self):
  with self.assertRaises(ValueError):validate_ts(b'\0'*4+reference_packet(0,PAT_SECTION))
 def test_continuity_wrap_and_gap(self):
  validate_ts(reference_packet(0,PAT_SECTION,15)+reference_packet(0,PAT_SECTION,0))
  with self.assertRaisesRegex(ValueError,'continuity'):validate_ts(reference_packet(0,PAT_SECTION,1)+reference_packet(0,PAT_SECTION,3))
 def test_adaptation_overflow_rejected(self):
  packet=bytearray(reference_packet(0,PAT_SECTION));packet[3]=0x30;packet[4]=184
  with self.assertRaisesRegex(ValueError,'Adaptation'):validate_ts(bytes(packet))
if __name__=='__main__':unittest.main()

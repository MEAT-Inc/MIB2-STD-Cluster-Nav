"""Offboard-only dual service descriptor tests. No unit access or advertisement."""
import unittest
from android_discovery_wire_fixture import add_cluster_services,message,uint,independent_decode
class PairTests(unittest.TestCase):
 def setUp(self):
  self.response=message(1,uint(1,1)+message(3,uint(1,3)+message(4,uint(1,1))))+message(1,uint(1,2)+message(4,message(1,b'\x17')))+message(100,b'unknown')
 def test_pair_preserves_original_and_matches_display(self):
  out=add_cluster_services(self.response,1,9,10,1);self.assertTrue(out.startswith(self.response))
  services=[independent_decode(v) for n,w,v in independent_decode(out) if n==1]
  self.assertEqual([next(v for n,w,v in s if n==1) for s in services],[1,2,9,10])
  video=independent_decode(next(v for n,w,v in services[-2] if n==3));inp=independent_decode(next(v for n,w,v in services[-1] if n==4))
  self.assertIn((6,0,1),video);self.assertIn((7,0,1),video);self.assertIn((5,0,1),inp)
  self.assertIn((1,2,b'\x17\x80\x80\x04'),inp)
  self.assertFalse(any(n in (2,3) for n,w,v in inp))
 def test_collisions_and_invalid_ids(self):
  for video,inp in ((1,10),(9,2),(9,9),(9,255),(9,0),(255,10)):
   with self.subTest(video=video,inp=inp),self.assertRaises(ValueError):add_cluster_services(self.response,1,video,inp)
 def test_invalid_or_ambiguous_video(self):
  for response in (self.response+message(1,uint(1,1)+message(3,message(4,b''))),b'\x0a\x80',uint(1,1)):
   with self.assertRaises(ValueError):add_cluster_services(response,1,9,10)
if __name__=='__main__':unittest.main()

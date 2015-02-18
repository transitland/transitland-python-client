"""geohash unit tests."""
import unittest
import tempfile
import zipfile
import glob
import os
import json

import geohash

class TestGeoHash(unittest.TestCase):
  tests = [
    ['xn76urwe1g9y', (35.681382017210126, 139.76608408614993)],
    ['9q8yykv7bpr4', (37.775799008086324, -122.41343496367335)],
    ['qgmpv9mkv4x0', (-25.34874997101724, 131.03038312867284)]
  ]

  def test_decode(self):
    for test, expect in self.tests:
      value = geohash.decode(test)
      self.assertAlmostEqual(value[0], expect[0])
      self.assertAlmostEqual(value[1], expect[1])
  
  def test_encode(self):
    for expect, test in self.tests:
      value = geohash.encode(test)
      self.assertAlmostEqual(value[0], expect[0])
      self.assertAlmostEqual(value[1], expect[1])
      
  def test_roundtrip(self):
    for test, expect in self.tests:
      encoded = geohash.decode(test)
      decoded = geohash.encode(encoded)
      # print "expect:", expect, encoded
      # print "test:", test, decoded
      assert test == decoded
      
if __name__ == '__main__':
    unittest.main()
"""Entity tests."""
import os
import unittest
import sys
import pprint

import entities

class TestOnestopOperator(unittest.TestCase):
  def setUp(self):
    self.path = os.path.join('examples', 'o-9qs-demotransitauthority.geojson')
  
  def test_from_json(self):
    agency = entities.OnestopOperator.from_json(self.path)
    assert agency.name() == 'Demo Transit Authority'
    assert agency.onestop() == 'o-9qs-demotransitauthority'
    assert len(agency.stops()) == 9
    assert len(agency.routes()) == 5
    assert 's-9qscwx8n60-nyecountyairportdemo' in [i.onestop() for i in agency.stops()]
    assert 'r-9qt1-50' in [i.onestop() for i in agency.routes()]
      
if __name__ == '__main__':
    unittest.main()
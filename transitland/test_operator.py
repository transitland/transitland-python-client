"""Test Operator."""
import unittest

import util
from operator import Operator

class TestOperator(unittest.TestCase):
  def setUp(self):
    self.expect = util.example_export()
  
  def _sanity(self, entity):
    """Perform sanity checks! After bootstrap_gtfs or from_json..."""
    # More extensive checks, since json export includes nearly everything.
    assert entity.geohash() == '9qs'
    assert entity.onestop() == self.expect['onestopId']
    assert len(entity.identifiers()) == 1
    # Routes
    assert len(entity.routes()) == 5
    expect = ['r-9qsczp-40', 'r-9qt1-50', 
      'r-9qsb-20', 'r-9qscy-30', 'r-9qscy-10']
    for i in entity.routes():
      assert i.onestop() in expect
      assert len(i.identifiers()) == 1
    # Stops
    assert len(entity.stops()) == 9
    for i in entity.stops():
      assert i.onestop() in self.expect['serves']
      assert len(i.identifiers()) == 1    

  def test_init(self):
    entity = Operator()
      
  def test_geohash(self):
    entity = util.example_feed().operator(self.expect['onestopId'])
    assert entity.geohash() == '9qs'
    
  def test_from_json(self):
    feed = util.example_feed()
    entity = util.example_feed().operator(self.expect['onestopId'])
    roundtrip = Operator.from_json(entity.json())
    self._sanity(roundtrip)
  
  def test_json(self):
    entity = util.example_feed().operator(self.expect['onestopId'])
    data = entity.json()
    for k in ['name','onestopId','type']:
      assert data[k] == self.expect[k]
    assert len(data['features']) == 14
  
  def test_routes(self): 
    entity = util.example_feed().operator(self.expect['onestopId'])
    assert len(entity.routes()) == 5

  def test_route(self):
    entity = util.example_feed().operator(self.expect['onestopId'])
    for i in entity.routes():
      assert entity.route(i.onestop())
    with self.assertRaises(ValueError):
      entity.route('none')

  def test_stops(self): 
    entity = util.example_feed().operator(self.expect['onestopId'])
    assert len(entity.stops()) == 9
    
  def test_stop(self):
    entity = util.example_feed().operator(self.expect['onestopId'])
    for i in entity.stops():
      assert entity.stop(i.onestop())
    with self.assertRaises(ValueError):
      entity.stop('none')

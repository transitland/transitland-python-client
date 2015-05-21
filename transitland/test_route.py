"""Test Route."""
import unittest

import util
from route import Route

class TestRoute(unittest.TestCase):
  def setUp(self):
    data = util.example_export()
    name = 'r-9qsb-20'
    feature = [i for i in data['features'] if i['onestopId'] == name]
    assert len(feature) == 1
    self.expect = feature[0]

  def test_init(self):
    entity = Route()
    
  def test_geohash(self):    
    entity = util.example_feed().route(self.expect['onestopId'])
    assert entity.geohash() == '9qsb'
    
  def test_json(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    data = entity.json()
    for k in ['name','onestopId','type']:
      assert data[k] == self.expect[k]
    assert data['operatedBy'] == self.expect['operatedBy']
    assert data['geometry']
    assert data['geometry']['type'] == 'MultiLineString'
    assert data['geometry']['coordinates']
    assert len(data['serves']) == 2
    assert len(data['identifiers']) == 1
    # assert data['identifiers'][0]['identifier'] == 'f-0-unknown-r-CITY'
  
  def test_operators(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    assert len(entity.operators()) == 1
    
  def test_operator(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    assert entity.operator(self.expect['operatedBy'])
  
  def test_stops(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    stops = entity.stops()
    assert len(stops) == 2
    for i in stops:
      assert i.onestop() in self.expect['serves']
  
  def test_stop(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    # print "test_stop:", self.expect['serves']
    # print [i.onestop() for i in entity.stops()]
    for i in self.expect['serves']:
      assert entity.stop(i)
    
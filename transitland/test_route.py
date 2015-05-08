"""Test Route."""
import unittest

import util
from route import Route

class TestRoute(unittest.TestCase):
  expect = {
    'geometry': {'coordinates': [[[-116.751677, 36.915682],
                                   [-116.761472, 36.914944],
                                   [-116.76821, 36.914893],
                                   [-116.768242, 36.909489],
                                   [-116.76218, 36.905697]],
                                  [[-116.76218, 36.905697],
                                   [-116.768242, 36.909489],
                                   [-116.76821, 36.914893],
                                   [-116.761472, 36.914944],
                                   [-116.751677, 36.915682]]],
                 'type': 'MultiLineString'},
   'identifiers': ['gtfs://unknown/r/CITY'],
   'name': '40',
   'onestopId': 'r-9qsczp-40',
   'operatedBy': 'o-9qs-demotransitauthority',
   'properties': {},
   'serves': ['s-9qsfnb5uz6-north~dndemo',
               's-9qscyz5vqg-doing~dndemo',
               's-9qsfp2212t-stagecoachhotel~casinodemo',
               's-9qsczn2rk0-emain~sirvingdemo',
               's-9qsfp00vhs-north~nademo'],
   'tags': {},
   'type': 'Feature'
 }
  
  def test_init(self):
    entity = Route()
    
  def test_geohash(self):    
    entity = util.example_feed().route(self.expect['onestopId'])
    assert entity.geohash() == '9qsczp'
    
  def test_json(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    data = entity.json()
    for k in ['name','onestopId','type']:
      assert data[k] == self.expect[k]
    assert data['operatedBy'] == self.expect['operatedBy']
    assert data['geometry']
    assert data['geometry']['type'] == 'MultiLineString'
    assert data['geometry']['coordinates']
    assert len(data['serves']) == 5
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
    assert len(stops) == 5
    for i in stops:
      assert i.onestop() in self.expect['serves']
  
  def test_stop(self):
    entity = util.example_feed().route(self.expect['onestopId'])
    print "test_stop:", self.expect['serves']
    print [i.onestop() for i in entity.stops()]
    for i in self.expect['serves']:
      assert entity.stop(i)
    
"""Test Operator."""
import unittest

import util
from operator import Operator

class TestOperator(unittest.TestCase):
  expect = {
    'geometry': {'coordinates': [[[-117.133162, 36.425288],
                                   [-116.40094, 36.641496],
                                   [-116.751677, 36.915682],
                                   [-116.76821, 36.914893],
                                   [-116.81797, 36.88108],
                                   [-117.133162, 36.425288]]],
                 'type': 'Polygon'},
   'identifiers': ['gtfs://unknown/o/DTA'],
   'name': 'Demo Transit Authority',
   'onestopId': 'o-9qs-demotransitauthority',
   'properties': {},
   'serves': ['s-9qscv9zzb5-bullfrogdemo',
               's-9qt0rnrkjt-amargosavalleydemo',
               's-9qscwx8n60-nyecountyairportdemo',
               's-9qkxnx40xt-furnacecreekresortdemo',
               's-9qscyz5vqg-doing~dndemo',
               's-9qsfp2212t-stagecoachhotel~casinodemo',
               's-9qsfp00vhs-north~nademo',
               's-9qsfnb5uz6-north~dndemo',
               's-9qsczn2rk0-emain~sirvingdemo'],
   'tags': {},
   'type': 'FeatureCollection'
  }
  
  def _sanity(self, entity):
    """Perform sanity checks! After from_gtfs or from_json..."""
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
  
  def test_from_gtfs(self):
    feed = util.example_gtfs_feed()
    try:
      feed.preload()
    except AttributeError, e:
      pass
    agency = feed.agency('DTA')
    try:
      agency.preload()
    except AttributeError, e:
      pass
    entity = Operator.from_gtfs(agency)
    self._sanity(entity)
    
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

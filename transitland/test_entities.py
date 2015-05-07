"""Entity unit tests."""
import os
import unittest
import sys
import pprint
import collections
import json
import tempfile

import mzgtfs.feed

import util
import entities
import errors

def example_feed(*args, **kw):
  return mzgtfs.feed.Feed(util.example_feed(*args, **kw))

def example_onestopfeed():
  feed = mzgtfs.feed.Feed(util.example_feed())
  onestopfeed = entities.OnestopFeed.from_gtfs(feed, name='test')
  return onestopfeed

class TestOnestopEntity(unittest.TestCase):
  expect = {
    'name':'foobar',
    'foo':'bar',
    'rab':'oof',
    'identifiers':['gtfs://test/s/ok']
  }
    
  def test_init(self):
    entity = entities.OnestopEntity(**self.expect)
  
  def test_name(self):
    entity = entities.OnestopEntity(**self.expect)
    assert entity.name() == self.expect['name']
  
  def test_mangle(self):
    entity = entities.OnestopEntity(**self.expect)
    assert entity.mangle('A b C {d%') == 'abcd'
    assert entity.mangle('ABCD') == 'abcd'
    assert entity.mangle('A&B@C:D') == 'a~b~c~d'

  def test_from_json(self):
    data = json.loads(json.dumps(self.expect))
    entity = entities.OnestopEntity.from_json(data)
    assert entity.name() == self.expect['name']
  
  def test_add_identifier(self):
    data = ['abc', 'def']
    entity = entities.OnestopEntity()
    for k in data:
      entity.add_identifier(k)
    assert len(entity.identifiers()) == 2
    for i in entity.identifiers():
      assert i in data
    with self.assertRaises(errors.OnestopExistingIdentifier):
      entity.add_identifier('abc')

  def test_merge(self):
    data = ['abc', 'def']
    entity1 = entities.OnestopEntity()
    entity1.add_identifier('abc')
    entity2 = entities.OnestopEntity()
    entity2.add_identifier('def')
    entity1.merge(entity2)
    assert len(entity1.identifiers()) == 2
    for i in entity1.identifiers():
      assert i in data

  def test_merge_identifiers(self):
    data = ['abc', 'def']
    entity = entities.OnestopEntity()
    for k in data:
      entity.add_identifier(k)
    
  # Graph stuff...
  def test_pclink(self):
    entity1 = entities.OnestopEntity()
    entity2 = entities.OnestopEntity()
    assert len(entity1.children) == 0
    assert len(entity2.parents) == 0
    entity1.pclink(entity1, entity2)
    assert len(entity1.children) == 1
    assert len(entity2.parents) == 1
    
  def test_add_child(self):
    entity1 = entities.OnestopEntity()
    entity2 = entities.OnestopEntity()
    entity1.add_child(entity2)
    assert len(entity1.children) == 1
    assert len(entity2.parents) == 1

  def test_add_parent(self):
    entity1 = entities.OnestopEntity()
    entity2 = entities.OnestopEntity()
    entity2.add_parent(entity1)
    assert len(entity1.children) == 1
    assert len(entity2.parents) == 1

  # TODO: these tests are not ideal.
  def test_geometry(self):
    entity = entities.OnestopEntity(**self.expect)
    assert entity.geometry() is None
  
  def test_tags(self):
    entity = entities.OnestopEntity(**self.expect)
    assert not entity.tags()
    assert hasattr(entity.tags(), 'keys')
  
  # ... the rest of Entity base methods require NotImplemetedError features.
  def test_onestop_notimplemented(self):
    # requires geohash() to be implemented.
    entity = entities.OnestopEntity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.id()
    with self.assertRaises(NotImplementedError):
      entity.onestop()
    
  def test_geom_notimplemented(self):
    # requires geohash() and point() to be implemented.
    entity = entities.OnestopEntity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.geohash()
    with self.assertRaises(NotImplementedError):
      entity.point()
    with self.assertRaises(NotImplementedError):
      entity.bbox()
      
  def test_load_dump_notimplemented(self):
    # requires json() to be implemented.
    entity = entities.OnestopEntity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entities.OnestopEntity.from_gtfs(example_feed())
    with self.assertRaises(NotImplementedError):
      entity.json()
    with self.assertRaises(NotImplementedError):
      entity.json_datastore()

class TestOnestopFeed(unittest.TestCase):
  expect = {
    'feedFormat': 'gtfs',
    'name': 'test',
    'onestopId': 'f-9qs-test',
    'operatorsInFeed': [
      {'gtfsAgencyId': 'demotransitauthority',
      'onestopId': 'o-9qs-demotransitauthority'}
    ],
    'sha1': '4e5e6a2668d12cca29c89a969d73e05e625d9596',
    'tags': {},
    'url': None
  }
  
  def _sanity(self, entity):
    """Sanity check after load from_json() / from_gtfs()"""
    assert entity.onestop() == self.expect['onestopId']
    assert entity.id() == self.expect['onestopId']
    assert entity.url() == self.expect['url']
    assert entity.sha1() == self.expect['sha1']
    assert entity.feedFormat() == self.expect['feedFormat']
    assert entity.name() == self.expect['name']
  
  # Feed implementes geohash(), so we will test many Entity base methods here.
  def test_id(self):
    entity = example_onestopfeed()
    assert entity.id() == self.expect['onestopId']
  
  def test_onestop(self):
    entity = example_onestopfeed()
    assert entity.onestop() == self.expect['onestopId']

  def test_onestop_maxlen(self):
    entity = example_onestopfeed()
    entity.data['name'] = 'maximumlength' * 10
    assert len(entity.data['name']) > entities.ONESTOP_LENGTH
    assert len(entity.onestop()) <= entities.ONESTOP_LENGTH

  # Other Entity base methods that only make sense to test here...
  def test_json(self):
    # Check result looks like self.expect.
    entity = example_onestopfeed()
    data = entity.json()
    for k in ('onestopId','name','url','sha1','feedFormat'):
      assert data[k] == self.expect[k]
    assert len(data['operatorsInFeed']) == 1
    assert 'o-9qs-demotransitauthority' in data['operatorsInFeed']
  
  def test_from_json(self):
    # TODO: more thorough testing here...
    entity = example_onestopfeed()
    roundtrip = entities.OnestopFeed.from_json(entity.json())
    self._sanity(roundtrip)

  def test_json_datastore(self):
    # Alternate JSON representation, for datastore...
    entity = example_onestopfeed()
    data = entity.json_datastore()
    assert 'identifiers' not in data
    assert 'features' not in data
    # assert data['tags']
    assert data['operatorsInFeed']
    # check without rels...
    data = entity.json_datastore(rels=False)
    assert 'serves' not in data
    assert 'doesNotServe' not in data
    assert 'servedBy' not in data
    assert 'notServedBy' not in data

  # Geometry and point are not implemented...
  def test_geometry(self):
    # TODO: Feed doesn't have geometry... convex hull like operator?
    entity = example_onestopfeed()
    assert entity.geometry() is None
    
  def test_point(self):
    entity = example_onestopfeed()
    with self.assertRaises(NotImplementedError):
      entity.point()
      
  def test_bbox(self):
    entity = example_onestopfeed()
    with self.assertRaises(NotImplementedError):
      entity.bbox()
  
  # Test OnestopFeed methods
  def test_url(self):
    # TODO: feed doesn't have url...
    entity = example_onestopfeed()
    assert entity.url() == self.expect['url']
    
  def test_sha1(self):
    entity = example_onestopfeed()
    assert entity.sha1() == self.expect['sha1']

  def test_feedFormat(self):
    entity = example_onestopfeed()
    assert entity.feedFormat() == self.expect['feedFormat']    
  
  # Test fetching...
  def test_download(self):
    # TODO: feed doesn't have url...
    entity = example_onestopfeed()
    f = tempfile.NamedTemporaryFile()
    with self.assertRaises(ValueError):
      entity.download(f.name)
  
  # Load / dump
  def test_from_gtfs(self):
    entity = example_onestopfeed()
    self._sanity(entity)
    # Check operators...
    assert len(entity.operators()) == 1
    o = list(entity.operators())[0]
    assert o.onestop() == 'o-9qs-demotransitauthority'
    assert len(o.routes()) == 5
    assert len(o.stops()) == 9

  # Graph
  def test_operators(self):
    entity = example_onestopfeed()
    assert len(entity.operators()) == len(self.expect['operatorsInFeed'])

  def test_operator(self):
    entity = example_onestopfeed()
    for i in self.expect['operatorsInFeed']:
      assert entity.operator(i['onestopId'])
    with self.assertRaises(ValueError):
      entity.operator('none')

  def test_operatorsInFeed(self):
    entity = example_onestopfeed()
    o = entity.operatorsInFeed()
    assert len(o) == 1
    assert 'o-9qs-demotransitauthority' in o
    
  def test_routes(self):
    entity = example_onestopfeed()
    routes = entity.routes()
    assert len(routes) == 5

  def test_route(self):
    entity = example_onestopfeed()
    for i in entity.routes():
      assert entity.route(i.onestop())
    with self.assertRaises(ValueError):
      entity.route('none')
    
  def test_stops(self):
    entity = example_onestopfeed()
    stops = entity.stops()
    assert len(stops) == 9

  def test_stop(self):
    entity = example_onestopfeed()
    for i in entity.stops():
      assert entity.stop(i.onestop())
    with self.assertRaises(ValueError):
      entity.stop('none')
    
class TestOnestopOperator(unittest.TestCase):
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
    entity = entities.OnestopOperator()
      
  def test_geohash(self):
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    assert entity.geohash() == '9qs'
  
  def test_from_gtfs(self):
    feed = mzgtfs.feed.Feed(util.example_feed())
    agency = feed.agency('DTA')
    agency.preload()
    entity = entities.OnestopOperator.from_gtfs(agency)
    self._sanity(entity)
    
  def test_from_json(self):
    feed = example_onestopfeed()
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    roundtrip = entities.OnestopOperator.from_json(entity.json())
    self._sanity(roundtrip)
  
  def test_json(self):
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    data = entity.json()
    for k in ['name','onestopId','type']:
      assert data[k] == self.expect[k]
    assert len(data['features']) == 14
  
  def test_routes(self): 
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    assert len(entity.routes()) == 5

  def test_route(self):
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    for i in entity.routes():
      assert entity.route(i.onestop())
    with self.assertRaises(ValueError):
      entity.route('none')

  def test_stops(self): 
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    assert len(entity.stops()) == 9
    
  def test_stop(self):
    entity = example_onestopfeed().operator(self.expect['onestopId'])
    for i in entity.stops():
      assert entity.stop(i.onestop())
    with self.assertRaises(ValueError):
      entity.stop('none')

class TestOnestopRoute(unittest.TestCase):
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
    entity = entities.OnestopRoute()
    
  def test_geohash(self):    
    entity = example_onestopfeed().route(self.expect['onestopId'])
    assert entity.geohash() == '9qsczp'
    
  def test_json(self):
    entity = example_onestopfeed().route(self.expect['onestopId'])
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
    entity = example_onestopfeed().route(self.expect['onestopId'])
    assert len(entity.operators()) == 1
    
  def test_operator(self):
    entity = example_onestopfeed().route(self.expect['onestopId'])
    assert entity.operator(self.expect['operatedBy'])
  
  def test_stops(self):
    entity = example_onestopfeed().route(self.expect['onestopId'])
    stops = entity.stops()
    assert len(stops) == 5
    for i in stops:
      assert i.onestop() in self.expect['serves']
  
  def test_stop(self):
    entity = example_onestopfeed().route(self.expect['onestopId'])
    print "test_stop:", self.expect['serves']
    print [i.onestop() for i in entity.stops()]
    for i in self.expect['serves']:
      assert entity.stop(i)
    
class TestOnestopStop(unittest.TestCase):
  expect = {
    'geometry': {'coordinates': [-116.76821, 36.914893], 'type': 'Point'},
    'identifiers': ['gtfs://unknown/s/NADAV'],
    'name': 'North Ave / D Ave N (Demo)',
    'onestopId': 's-9qsfnb5uz6-north~dndemo',
    'properties': {},
    'servedBy': ['o-9qs-demotransitauthority'],
    'tags': {},
    'type': 'Feature'
  }

  def test_init(self):
    entity = entities.OnestopStop()
    
  def test_mangle(self):
    entity = entities.OnestopStop(**self.expect)
    assert entity.mangle('Test Street') == 'test'
    assert entity.mangle('Test St') == 'test'
    assert entity.mangle('Test St.') == 'test'
    assert entity.mangle('Test Avenue') == 'test'
    assert entity.mangle('Test Ave') == 'test'
    assert entity.mangle('Test Ave.') == 'test'
  
  def test_geohash(self):
    entity = example_onestopfeed().stop(self.expect['onestopId'])
    assert entity.geohash() == '9qsfnb5uz6'

  def test_point(self):
    entity = example_onestopfeed().stop(self.expect['onestopId'])
    expect = [-116.76821, 36.914893]
    for i,j in zip(entity.point(), expect):
      self.assertAlmostEqual(i,j)

  def test_bbox(self):
    entity = example_onestopfeed().stop(self.expect['onestopId'])
    expect = [-116.76821, 36.914893, -116.76821, 36.914893]
    for i,j in zip(entity.bbox(), expect):
      self.assertAlmostEqual(i,j)
      
  def test_json(self):
    entity = example_onestopfeed().stop(self.expect['onestopId'])
    data = entity.json()
    for k in ['name','onestopId','type']:
      assert data[k] == self.expect[k]
    assert len(data['servedBy']) == 1
    assert data['servedBy'][0] == self.expect['servedBy'][0]
    assert data['geometry']
    assert data['geometry']['type'] == 'Point'
    assert data['geometry']['coordinates']
    assert len(data['identifiers']) == 1
    # assert data['identifiers'][0]['identifier'] == 'f-0-unknown-s-NADAV'
  
  def test_operators(self):
    entity = example_onestopfeed().stop(self.expect['onestopId'])
    assert len(entity.operators()) == len(self.expect['servedBy'])

  def test_operator(self):
    entity = example_onestopfeed().stop(self.expect['onestopId'])
    for i in self.expect['servedBy']:
      assert entity.operator(i)

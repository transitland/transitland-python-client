"""Test Feed."""
import unittest
import os
import tempfile
import json

import util
from feed import Feed

class TestFeed(unittest.TestCase):
  def setUp(self):
    self.filename = os.path.join(util.example_registry(), 'feeds', 'f-9qs-dta.json')
    with open(self.filename) as f:
      self.expect = json.load(f)
    self.url = 'file://%s'%os.path.abspath(util.example_gtfs_feed_path())
    self.sha1_gtfs = '4e5e6a2668d12cca29c89a969d73e05e625d9596'
    self.sha1_feed = 'c0406d30424111404d6b2fa9ade7f9fc218f5ee8'
  
  def _sanity(self, entity):
    """Sanity check after load from_json() / from_gtfs()"""
    assert entity.onestop() == self.expect['onestopId']
    assert entity.id() == self.expect['onestopId']
    assert entity.url() == self.expect['url']
    assert entity.feedFormat() == self.expect['feedFormat']
    # assert entity.name() == self.expect['name']
  
  # Feed implementes geohash(), so we will test many Entity base methods here.
  def test_id(self):
    entity = util.example_feed()
    assert entity.id() == self.expect['onestopId']
  
  def test_onestop(self):
    entity = util.example_feed()
    assert entity.onestop() == self.expect['onestopId']

  def test_onestop_maxlen(self):
    entity = util.example_feed()
    entity.data['name'] = 'maximumlength' * 10
    assert len(entity.data['name']) > util.ONESTOP_LENGTH
    assert len(entity.make_onestop()) <= util.ONESTOP_LENGTH

  # Other Entity base methods that only make sense to test here...
  def test_json(self):
    # Check result looks like self.expect.
    entity = util.example_feed()
    data = entity.json()
    for k in ('onestopId','url','feedFormat'):
      assert data[k] == self.expect[k]
    assert len(data['operatorsInFeed']) == 1
    assert data['operatorsInFeed'][0]['onestopId'] == 'o-9qs-demotransitauthority'
  
  def test_from_json(self):
    # TODO: more thorough testing here...
    entity = util.example_feed()
    roundtrip = Feed.from_json(entity.json())
    self._sanity(roundtrip)

  # Geometry and point are not implemented...
  def test_geometry(self):
    # TODO: Feed doesn't have geometry... convex hull like operator?
    entity = util.example_feed()
    assert entity.geometry() is None
    
  def test_point(self):
    entity = util.example_feed()
    with self.assertRaises(NotImplementedError):
      entity.point()
      
  def test_bbox(self):
    entity = util.example_feed()
    with self.assertRaises(NotImplementedError):
      entity.bbox()
  
  # Test OnestopFeed methods
  def test_url(self):
    # TODO: feed doesn't have url...
    entity = util.example_feed()
    assert entity.url() == self.expect['url']
    
  def test_feedFormat(self):
    entity = util.example_feed()
    assert entity.feedFormat() == self.expect['feedFormat']    
  
  # Test fetching...
  def test_download_no_url(self):
    entity = util.example_feed()
    f = tempfile.NamedTemporaryFile()
    with self.assertRaises(ValueError):
      entity.download(f.name)
  
  def test_download(self):
    # Download the file, then download again to verify cache.
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    entity = util.example_feed()
    entity.data['url'] = self.url
    entity.download(f.name, cache=False)
    assert util.sha1file(f.name) == self.sha1_gtfs

  def test_download_badsha1(self):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write('asdf')
    f.close()
    assert util.sha1file(f.name) != self.sha1_gtfs
    entity = util.example_feed()
    entity.data['url'] = self.url
    entity.download(f.name, verify=True, sha1=self.sha1_gtfs)
    assert util.sha1file(f.name) == self.sha1_gtfs
  
  # Load / dump
  def test_from_gtfs(self):
    entity = util.example_feed()
    self._sanity(entity)
    # Check operators...
    assert len(entity.operators()) == 1
    o = list(entity.operators())[0]
    assert o.onestop() == 'o-9qs-demotransitauthority'
    assert len(o.routes()) == 5
    assert len(o.stops()) == 9

  def test_load_gtfs(self):
    gtfs_feed = util.example_gtfs_feed()
    feed = util.example_registry_feed()
    feed.load_gtfs(gtfs_feed)
    self._sanity(feed)

  def test_load_gtfs_onestop_id(self):
    onestop_id = 'o-9qs-test'
    gtfs_feed = util.example_gtfs_feed()
    feed = util.example_registry_feed()
    feed.data['operatorsInFeed'] = [{
			"gtfsAgencyId": "DTA",
			"onestopId": onestop_id
    }]
    feed.load_gtfs(gtfs_feed)
    assert len(feed.operators()) == 1
    o = list(feed.operators())[0]
    assert o.onestop() == onestop_id

  # Graph
  def test_operators(self):
    entity = util.example_feed()
    assert len(entity.operators()) == len(self.expect['operatorsInFeed'])

  def test_operator(self):
    entity = util.example_feed()
    for i in self.expect['operatorsInFeed']:
      assert entity.operator(i['onestopId'])
    with self.assertRaises(ValueError):
      entity.operator('none')

  def test_operatorsInFeed(self):
    entity = util.example_feed()
    o = entity.operatorsInFeed()
    assert len(o) == 1
    assert o[0]['onestopId'] == 'o-9qs-demotransitauthority'
    assert o[0]['gtfsAgencyId'] == 'DTA'
    
  def test_routes(self):
    entity = util.example_feed()
    routes = entity.routes()
    assert len(routes) == 5

  def test_route(self):
    entity = util.example_feed()
    for i in entity.routes():
      assert entity.route(i.onestop())
    with self.assertRaises(ValueError):
      entity.route('none')
    
  def test_stops(self):
    entity = util.example_feed()
    stops = entity.stops()
    assert len(stops) == 9

  def test_stop(self):
    entity = util.example_feed()
    for i in entity.stops():
      assert entity.stop(i.onestop())
    with self.assertRaises(ValueError):
      entity.stop('none')
    
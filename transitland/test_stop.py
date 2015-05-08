"""Test Stop."""
import unittest

import util
from stop import Stop

class TestStop(unittest.TestCase):
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
    entity = Stop()
    
  def test_mangle(self):
    entity = Stop(**self.expect)
    assert entity.mangle('Test Street') == 'test'
    assert entity.mangle('Test St') == 'test'
    assert entity.mangle('Test St.') == 'test'
    assert entity.mangle('Test Avenue') == 'test'
    assert entity.mangle('Test Ave') == 'test'
    assert entity.mangle('Test Ave.') == 'test'
  
  def test_geohash(self):
    entity = util.example_feed().stop(self.expect['onestopId'])
    assert entity.geohash()[:10] == '9qsfnb5uz6'

  def test_point(self):
    entity = util.example_feed().stop(self.expect['onestopId'])
    expect = [-116.76821, 36.914893]
    for i,j in zip(entity.point(), expect):
      self.assertAlmostEqual(i,j)

  def test_bbox(self):
    entity = util.example_feed().stop(self.expect['onestopId'])
    expect = [-116.76821, 36.914893, -116.76821, 36.914893]
    for i,j in zip(entity.bbox(), expect):
      self.assertAlmostEqual(i,j)
      
  def test_json(self):
    entity = util.example_feed().stop(self.expect['onestopId'])
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
    entity = util.example_feed().stop(self.expect['onestopId'])
    assert len(entity.operators()) == len(self.expect['servedBy'])

  def test_operator(self):
    entity = util.example_feed().stop(self.expect['onestopId'])
    for i in self.expect['servedBy']:
      assert entity.operator(i)

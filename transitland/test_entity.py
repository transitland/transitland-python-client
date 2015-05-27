"""Test base entity."""
import json
import unittest

import errors
import util
from entities import Entity

class TestEntity(unittest.TestCase):
  expect = {
    'name':'foobar',
    'foo':'bar',
    'rab':'oof',
    'identifiers':['gtfs://test/s/ok']
  }
    
  def test_init(self):
    entity = Entity(**self.expect)
  
  def test_name(self):
    entity = Entity(**self.expect)
    assert entity.name() == self.expect['name']
  
  def test_mangle(self):
    entity = Entity(**self.expect)
    assert entity.mangle('A b C {d%') == 'abcd'
    assert entity.mangle('ABCD') == 'abcd'
    assert entity.mangle('A&B@C:D') == 'a~b~c~d'

  def test_from_json(self):
    data = json.loads(json.dumps(self.expect))
    entity = Entity.from_json(data)
    assert entity.name() == self.expect['name']
  
  def test_add_identifier(self):
    data = ['abc', 'def']
    entity = Entity()
    for k in data:
      entity.add_identifier(k)
    assert len(entity.identifiers()) == 2
    for i in entity.identifiers():
      assert i in data
    with self.assertRaises(errors.ExistingIdentifierError):
      entity.add_identifier('abc')

  def test_merge(self):
    data = ['abc', 'def']
    entity1 = Entity()
    entity1.add_identifier('abc')
    entity2 = Entity()
    entity2.add_identifier('def')
    entity1.merge(entity2)
    assert len(entity1.identifiers()) == 2
    for i in entity1.identifiers():
      assert i in data

  def test_merge_identifiers(self):
    data = ['abc', 'def']
    entity = Entity()
    for k in data:
      entity.add_identifier(k)
    
  # Graph stuff...
  def test_pclink(self):
    entity1 = Entity()
    entity2 = Entity()
    assert len(entity1.children) == 0
    assert len(entity2.parents) == 0
    entity1.pclink(entity1, entity2)
    assert len(entity1.children) == 1
    assert len(entity2.parents) == 1
    
  def test_add_child(self):
    entity1 = Entity()
    entity2 = Entity()
    entity1.add_child(entity2)
    assert len(entity1.children) == 1
    assert len(entity2.parents) == 1

  def test_add_parent(self):
    entity1 = Entity()
    entity2 = Entity()
    entity2.add_parent(entity1)
    assert len(entity1.children) == 1
    assert len(entity2.parents) == 1

  # TODO: these tests are not ideal.
  def test_geometry(self):
    entity = Entity(**self.expect)
    assert entity.geometry() is None
  
  def test_tags(self):
    entity = Entity(**self.expect)
    assert not entity.tags()
    assert hasattr(entity.tags(), 'keys')
  
  # ... the rest of Entity base methods require NotImplemetedError features.
  def test_onestop_notimplemented(self):
    # requires geohash() to be implemented.
    entity = Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.id()
    with self.assertRaises(NotImplementedError):
      entity.onestop()
    
  def test_geom_notimplemented(self):
    # requires geohash() and point() to be implemented.
    entity = Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.geohash()
    with self.assertRaises(NotImplementedError):
      entity.point()
    with self.assertRaises(NotImplementedError):
      entity.bbox()
      
  def test_load_dump_notimplemented(self):
    # requires json() to be implemented.
    entity = Entity(**self.expect)
    with self.assertRaises(NotImplementedError):
      entity.json()

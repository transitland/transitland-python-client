"""Base Transitland Entity."""
import json

import mzgeohash

import geom
import util
import errors

class Entity(object):
  """A Transitland Entity."""  
  # OnestopID prefix.
  onestop_type = None

  def __init__(self, **data):
    """Set name, Onestop ID, and geometry."""
    if 'onestop_id' in data:
      data['onestopId'] = data.pop('onestop_id')
    data['tags'] = data.get('tags') or {}
    self.data = data
    self.parents = set()
    self.children = set()

  # Basic ID, name, geometry...    
  def name(self):
    """A reasonable display name for the entity."""
    return self.data.get('name')
  
  def id(self):
    """Alias to onestop()"""
    return self.onestop()

  def onestop(self):
    """Return the Onestop ID for this entity."""
    return self.data.get('onestopId') or self.make_onestop()

  def make_onestop(self, geohash=None, name=None):
    geohash = geohash or self.geohash()
    name = self.mangle(name or self.name())
    # Check maximum length.
    onestop = '%s-%s-%s'%(
      self.onestop_type, 
      geohash[:util.GEOHASH_LENGTH], 
      name
    )
    return onestop[:util.ONESTOP_LENGTH]

  def mangle(self, s):
    """Mangle a string into a Onestop component."""
    s = s.lower()
    for a,b in util.REPLACE_CHAR:
      s = a.sub(b,s)
    s = s.strip() 
    return s

  # Entity geometry.
  def geohash(self):
    """Return the geohash for this entity."""
    raise NotImplementedError

  def geometry(self):
    """Return a GeoJSON-type geometry for this entity."""
    # TODO: Right now, this has to be supplied by GTFS Entity...
    return self.data.get('geometry')

  def point(self):
    """Return a point for this entity."""
    raise NotImplementedError
  
  def bbox(self):
    """Return a bounding box for this entity."""
    c = self.point()
    return [c[0], c[1], c[0], c[1]]
  
  # Load from GTFS entity.
  @classmethod
  def from_gtfs(cls, gtfs_entity, feedid, **kw):
    entity = cls(
      name=gtfs_entity.name(),
      geometry=gtfs_entity.geometry(),
      **kw
    )
    entity.add_identifier(gtfs_entity.feedid(feedid))
    entity.add_tags_gtfs(gtfs_entity)
    return entity
  
  # Load from JSON.
  @classmethod
  def from_json(cls, data):
    return cls(**data)

  def json(self):
    """Return a GeoJSON representation of this entity."""
    raise NotImplementedError
  
  # Tags and identifiers
  def tags(self):
    return self.data['tags']

  def tag(self, key):
    return self.data['tags'].get(key)

  def identifiers(self):
    return self.data.get('identifiers') or []

  def set_tag(self, key, value):
    self.add_tags({key:value})

  def add_tags(self, tags):
    self.data['tags'].update(tags)

  def add_tags_gtfs(self, gtfs_entity):
    pass

  def add_identifier(self, identifier):
    """Add GTFS data to the set of identifiers."""
    if not self.data.get('identifiers'):
      self.data['identifiers'] = []
    if identifier not in self.data['identifiers']:
      self.data['identifiers'].append(identifier)
  
  # Rename
  def merge(self, item):
    """Merge data into identifiers."""
    for identifier in item.identifiers():
      self.add_identifier(identifier)
    # merge name and geometry.
    if 'name' in item.data:
      self.data['name'] = item.data['name']
    if 'geometry' in item.data:
      self.data['geometry'] = item.data['geometry']
    # merge tags
    for k,v in item.tags().items():
      self.set_tag(k,v)
    # merge relations
    relkeys = ['serves', 'servedBy', 'operatedBy']
    for relkey in relkeys:
      if (relkey in self.data) or (relkey in item.data):
        a = set(self.data.get(relkey, []))
        b = set(item.data.get(relkey, []))
        self.data[relkey] = sorted(a | b)

  # Graph.
  def pclink(self, parent, child):
    """Create a parent-child relationship."""
    parent.children.add(child)
    child.parents.add(parent)

  # ... children
  def add_child(self, child):
    """Add a child relationship."""
    self.pclink(self, child)

  # ... parents
  def add_parent(self, parent):
    """Add a parent relationship."""
    self.pclink(parent, self)  
    
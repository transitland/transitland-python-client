"""Base Transitland Entity."""
import json

import mzgtfs.feed
import mzgtfs.util
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
    
  def make_onestop(self):
    # Check maximum length.
    onestop = '%s-%s-%s'%(
      self.onestop_type, 
      self.geohash()[:util.GEOHASH_LENGTH], 
      self.mangle(self.name())
    )
    return onestop[:util.ONESTOP_LENGTH]

  def mangle(self, s):
    """Mangle a string into a Onestop component."""
    s = s.lower()
    for a,b in util.REPLACE_CHAR:
      s = a.sub(b,s)
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
  
  # Load from GTFS or from JSON.
  @classmethod
  def from_gtfs(cls, feed, debug=False):
    raise NotImplementedError

  @classmethod
  def from_json(cls, data):
    return cls(**data)

  def json(self):
    """Return a GeoJSON representation of this entity."""
    raise NotImplementedError
  
  def json_datastore(self, rels=True):
    """Return a GeoJSON representation for the Transitland Datastore."""
    # Todo: Longer discussion on formats...
    data = self.json()
    skip = ['features', 'identifiers']
    if not rels:
      skip += [
        'serves', 
        'doesNotServe', 
        'servedBy', 
        'notServedBy', 
        # 'operatedBy' # required!
      ]
    for key in skip:
      data.pop(key, None)
    return data

  # Tags and identifiers
  def tags(self):
    return self.data.get('tags') or {}

  def identifiers(self):
    return self.data.get('identifiers') or []

  def set_tag(self, key, value):
    self.add_tags({key:value})

  def add_tags(self, tags):
    if 'tags' not in self.data:
      self.data['tags'] = {}
    self.data['tags'].update(tags)

  def add_identifier(self, identifier):
    """Add GTFS data to the set of identifiers."""
    if 'identifiers' not in self.data:
      self.data['identifiers'] = []
    if identifier in self.data['identifiers']:
      raise errors.ExistingIdentifierError(
        "Identifier already present: %s"%identifier
      )
    self.data['identifiers'].append(identifier)
  
  # Rename
  def merge(self, item, ignore_existing=True):
    """Merge data into identifiers."""
    for identifier in item.identifiers():
      try:
        self.add_identifier(identifier)
      except errors.ExistingIdentifierError, e:
        if ignore_existing:
          pass
        else:
          raise
    # merge name and geometry.
    if 'name' in item.data:
      self.data['name'] = item.data['name']
    if 'geometry' in item.data:
      self.data['geometry'] = item.data['geometry']
    # merge relations
    relkeys = ['serves', 'servedBy', 'operatedBy', 'operatorsInFeed']
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
    
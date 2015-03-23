"""Onestop entities."""
import collections
import json
import copy
import re

import mzgtfs.entities
import mzgeohash

import errors

# Regexes
REPLACE_CHAR = [
  # replace &, @, and / with ~
  [r':','~'], 
  [r'&','~'], 
  [r'@','~'],
  [r'\/','~'],
  # replace every other special char
  [r'[^~0-9a-zA-Z]+', '']
]
REPLACE_CHAR = [[re.compile(i[0]), i[1]] for i in REPLACE_CHAR]

REPLACE_ABBR = [
  'street', 
  'st',
  'sts',
  'ctr',
  'center',
  'drive',
  'dr',
  'ave', 
  'avenue', 
  'av',
  'boulevard', 
  'blvd', 
  'road', 
  'rd', 
  'alley', 
  'aly', 
  'way', 
  'parkway', 
  'pkwy', 
  'lane',
  'ln',
  'hwy',
  'court',
  'ct',
]
REPLACE_ABBR = [[re.compile(r'\b%s\b'%i), ''] for i in REPLACE_ABBR]

##### Geohash utility functions #####

def geohash_features(features):
  # Filter stops without valid coordinates...
  points = [feature.point() for feature in features if feature.point()]
  if not points:
    raise errors.OnestopNoPoints("Not enough points.")
  c = centroid_points(points)
  return mzgeohash.neighborsfit(c, points)
  
def centroid_points(points):
  """Return the lon,lat centroid for features."""
  # Todo: Geographic center, or simple average?
  import ogr, osr
  multipoint = ogr.Geometry(ogr.wkbMultiPoint)
  # spatialReference = osr.SpatialReference() ...
  for point in points:
    p = ogr.Geometry(ogr.wkbPoint)
    p.AddPoint(point[1], point[0])
    multipoint.AddGeometry(p)
  point = multipoint.Centroid()
  return (point.GetY(), point.GetX())

##### Entities #####

class OnestopEntity(object):
  """A OnestopEntity."""  
  # OnestopID prefix.
  onestop_type = None

  def __init__(self, name=None, onestop=None, geometry=None, **kwargs):
    """Set name, OnestopID, and geometry."""
    super(OnestopEntity, self).__init__(
      name=name, 
      onestop=onestop, 
      geometry=geometry
    )
    self.url = kwargs.get('url')
    self.feedFormat = kwargs.get('feedFormat', 'gtfs')
  
  @classmethod
  def from_json(cls, filename):
    raise NotImplementedError
    
  @classmethod
  def from_gtfs(cls, filename):
    raise NotImplementedError

  def pclink(self, parent, child):
    """Create a parent-child relationship."""
    parent.children.add(child)
    child.parents.add(parent)

  def name(self):
    """A reasonable display name for the entity."""
    return self._name
    
  def bbox(self):
    """Return a bounding box for this entity."""
    raise NotImplementedError
  
  def geometry(self):
    """Return a GeoJSON-type geometry for this entity."""
    return self._geometry

  def geohash(self):
    """Return the geohash for this entity."""
    raise NotImplementedError
  
  def json(self):
    """Return a GeoJSON representation of this entity."""
    raise NotImplementedError
    
  # References to GTFS entities.
  def identifiers(self):
    return self._identifiers
    
  def add_identifier(self, identifier, tags):
    """Add original GTFS data."""    
    if identifier in [i['identifier'] for i in self._identifiers]:
      raise errors.OnestopExistingIdentifier(
        "Identifier already present: %s"%identifier
      )
    self._identifiers.append({
      'identifier': identifier,
      'tags': tags
    })
  
  def merge(self, item):
    """Merge identifiers."""
    for i in item.identifiers():
      self.add_identifier(identifier=i['identifier'], tags=i['tags'])
  
  # Onestop methods
  def mangle(self, s):
    """Mangle a string into an Onestop component."""
    s = s.lower()
    for a,b in REPLACE_CHAR:
      s = a.sub(b,s)
    return s    

  def onestop(self, cache=True):
    """Return the OnestopID for this entity."""
    # cache...
    if cache and getattr(self, '_onestop', None):
      return self._onestop
    # Create if necessary.
    self._onestop = '%s-%s-%s'%(
      self.onestop_type, 
      self.geohash(), 
      self.mangle(self.name())
    )
    return self._onestop
  
class OnestopOperator(OnestopEntity):
  """Onestop Operator."""
  onestop_type = 'o'
  
  @classmethod
  def from_gtfs(cls, gtfs_agency):
    """Load Onestop Operator from a GTFS Agency."""
    agency = cls(name=gtfs_agency.name())
    agency.add_identifier(gtfs_agency.feedid(), gtfs_agency.data)
    # Group stops
    stops = {}
    for i in gtfs_agency.stops():
      stop = OnestopStop(
        name=i.name(), 
        geometry=i.geometry()
      )
      key = stop.onestop()
      if key not in stops:
        stops[key] = stop
      # Hack to maintain ref to stop
      i._onestop_parent = stops[key]
      stops[key].add_identifier(i.feedid(), i.data)
    # Routes
    routes = {}
    for i in gtfs_agency.routes():
      route = OnestopRoute(
        name=i.name(),
        geometry=i.geometry()
      )
      if not i.stops():
        print "Yikes! No stops! Skipping this route."
        continue
      for j in i.stops():
        route.pclink(route, j._onestop_parent)
      key = route.onestop()
      if key in routes:
        # raise KeyError("Route already exists!: %s"%key)
        # Hack
        print "Route already exists, setting temp fix..."
        route._name = '%s~1'%route._name
        route._onestop = None
        key = route.onestop()
        print "set key to:", key
        assert key not in routes
      route.pclink(agency, route)
      route.add_identifier(i.feedid(), i.data)
      routes[key] = route
    # Return agency
    return agency

  @classmethod
  def from_json(cls, filename):
    """Load Onestop Operator from GeoJSON."""
    with open(filename) as f:
      data = json.load(f)
    agency = cls(
      name=data['name'],
      onestop=data['onestopId']
    )
    agency._identifiers = data['identifiers']
    agency._tags = data['tags']
    # Add stops
    stops = {}
    for feature in data['features']:
      if feature['onestopId'].startswith('s'):
        stop = OnestopStop(
          name=feature['name'], 
          onestop=feature['onestopId'],
          geometry=feature['geometry']
        )
        stop._identifiers = feature['identifiers']
        stop._tags = feature['tags']
        stops[stop.onestop()] = stop
    # Add routes
    for feature in data['features']:
      if feature['onestopId'].startswith('r'):
        route = OnestopRoute(
          name=feature['name'],
          onestop=feature['onestopId'],
          geometry=feature['geometry']
        )
        route._identifiers = feature['identifiers']
        route._tags = feature['tags']
        # Get stop by id, add as child.
        for stop in feature['serves']:
          route.pclink(route, stops[stop])
        agency.pclink(agency, route)
    return agency

  def geohash(self):
    return geohash_features(self.stops())
    
  def json(self):
    return {
      'type': 'FeatureCollection',
      'properties': {},
      'name': self.name(),
      'tags': self._tags,
      'identifiers': self.identifiers(),
      'onestopId': self.onestop(),
      'serves': [i.onestop() for i in self.stops()],
      'features': [i.json() for i in self.routes() | self.stops()]
    }

  def routes(self):
    return self.children
  
  def stops(self):
    stops = set()
    for i in self.routes():
      stops |= i.stops()
    return stops  
        
class OnestopRoute(OnestopEntity):
  onestop_type = 'r'
  
  def geohash(self):
    """Return 10 characters of geohash."""
    return geohash_features(self.stops())

  def json(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self._tags,
      'identifiers': self.identifiers(),
      'operatedBy': [i.onestop() for i in self.agencies()][0],
      'serves': [i.onestop() for i in self.stops()],
    }
    
  def agencies(self):
    return self.parents

  def stops(self):
    return self.children  

class OnestopStop(OnestopEntity):
  onestop_type = 's'
  
  def mangle(self,s):
    """Also replace common road abbreviations."""
    s = s.lower()
    for a,b in REPLACE_ABBR:
      s = a.sub(b,s)
    for a,b in REPLACE_CHAR:
      s = a.sub(b,s)
    return s    

  def geohash(self):
    """Return 10 characters of geohash."""
    return mzgeohash.encode(self.point())[:10]
    
  def json(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self._tags,
      'identifiers': self.identifiers(),
      'servedBy': [i.onestop() for i in self.agencies()],
    }

  # Work with other interfaces
  def point(self):
    """Return stop point."""
    return self.geometry()['coordinates']
  
  def agencies(self):
    agencies = set()
    for i in self.parents:
      agencies |= i.parents
    return agencies

"""Onestop entities."""
import collections
import json
import copy
import re

import mzgtfs.entities
import mzgeohash

# Regexes
REPLACE = [
  [r'\'',''],
  [r'\.',''],
  [r' - ',':'],
  [r'&',':'],
  [r'@',':'],
  [r'\/',':'],
  [r' ','']
]
ABBR = [
  'street', 
  'st',
  'sts',
  'ctr',
  'center',
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
REPLACE_ABBR = [[r'\b%s\b'%i, ''] for i in ABBR]

def geohash_features(features):
  # Filter stops without valid coordinates...
  points = [feature.point() for feature in features if feature.point()]
  if not points:
    raise Exception("Not enough points.")
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

  def __init__(self, name=None, point=None):
    self._identifiers = {}
    self._tags = {}
    self._name = name
    self._point = point
    self.parents = set()
    self.children = set()

  def pclink(self, parent, child):
    parent.children.add(child)
    child.parents.add(parent)

  def name(self):
    """A reasonable display name for the entity."""
    return self._name
    
  def point(self):
    """Return a point geometry for this entity."""
    return self._point
    
  def bbox(self):
    """Return a bounding box for this entity."""
    raise NotImplementedError
  
  def geometry(self):
    """Return a GeoJSON-type geometry for this entity."""
    raise NotImplementedError

  def geohash(self):
    """Return the geohash for this entity."""
    raise NotImplementedError
  
  def geojson(self):
    """Return a GeoJSON representation of this entity."""
    raise NotImplementedError
    
  # References to GTFS entities.
  def identifiers(self):
    ret = []
    for k,v in self._identifiers.items():
      c = copy.copy(v.data)
      c['identifier'] = k
      ret.append(c)
    return ret
    
  def add_identifier(self, entity):
    # hack
    entity._onestop_parent = self 
    self._identifiers[entity.feedid()] = entity
  
  # Onestop methods
  def mangle(self, s):
    """Mangle a string into an identifier."""
    s = s.lower()
    for a,b in REPLACE:
      s = re.sub(a,b,s)
    return s    

  def onestop(self):
    """Return the OnestopID for this entity."""
    return '%s-%s-%s'%(
      self.onestop_type, 
      self.geohash(), 
      self.mangle(self.name())
    )

class OnestopAgency(OnestopEntity):
  onestop_type = 'o'
  
  @classmethod
  def from_gtfs(cls, gtfs_agency):
    """Create a Onestop Agency from a GTFS Agency."""
    agency = cls(name=gtfs_agency.name())
    agency.add_identifier(gtfs_agency)
    # Group stops
    stops = {}
    for i in gtfs_agency.stops():
      stop = OnestopStop(name=i.name(), point=i.point())
      key = stop.onestop()
      if key in stops:
        stops[key].add_identifier(i)
      else:
        stop.add_identifier(i)
        stops[key] = stop
    # Routes
    routes = {}
    for i in gtfs_agency.routes():
      route = OnestopRoute(name=i.name())
      for j in i.stops():
        route.pclink(route, j._onestop_parent)
      key = route.onestop()
      if key in routes:
        raise KeyError("Route already exists!")
      else:
        route.pclink(agency, route)
        route.add_identifier(i)
        routes[key] = route
    # Return agency
    return agency
    
  def geojson(self):
    return {
      'type': 'FeatureCollection',
      'properties': {},
      'name': self.name(),
      'tags': self._tags,
      'identifiers': self.identifiers(),
      'routes': [i.geojson() for i in self.routes()],
      'stops': [i.geojson() for i in self.stops()]
    }
    
  def routes(self):
    return self.children
  
  def stops(self):
    stops = set()
    for i in self.children:
      stops |= i.children
    return stops  
    
  def geohash(self):
    return 'agency'  
    
class OnestopRoute(OnestopEntity):
  onestop_type = 'r'
  
  def geohash(self):
    """Return 10 characters of geohash."""
    return geohash_features(self.children)

  def geojson(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self._tags,
      'identifiers': self.identifiers(),
      'operatedBy': [i.onestop() for i in self.parents][0],
      'serves': [i.onestop() for i in self.children],
    }

  def geometry(self):
    return {}

class OnestopStop(OnestopEntity):
  onestop_type = 's'
  
  def mangle(self,s):
    """Also replace common road abbreviations."""
    s = s.lower()
    for a,b in REPLACE:
      s = re.sub(a,b,s)
    for a,b in REPLACE_ABBR:
      s = re.sub(a,b,s)
    return s    

  def geohash(self):
    """Return 10 characters of geohash."""
    return mzgeohash.encode(self.point())[:10]
    
  def geojson(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self._tags,
      'identifiers': self.identifiers(),
      'servedBy': [i.onestop() for i in self.parents],
      'serves': [i.onestop() for i in self.children],
    }
  
  def geometry(self):
    return {
      "type": 'Point',
      "coordinates": self.point(),
    }
    
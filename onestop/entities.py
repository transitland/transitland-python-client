"""Onestop entities."""
import collections
import json
import copy
import re

import geom
import util
import errors

import mzgtfs.feed
import mzgtfs.util
import mzgeohash

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

##### Entities #####

class OnestopEntity(object):
  """A OnestopEntity."""  
  # OnestopID prefix.
  onestop_type = None

  def __init__(self, **data):
    """Set name, OnestopID, and geometry."""
    self.identifiers = data.pop('identifiers', [])
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

  def onestop(self, cache=True):
    """Return the OnestopID for this entity."""
    # Cache...
    if cache and 'onestopId' in self.data:
      return self.data.get('onestopId')
    # Create if necessary.
    self.data['onestopId'] = '%s-%s-%s'%(
      self.onestop_type, 
      self.geohash(), 
      self.mangle(self.name())
    )
    return self.data['onestopId']

  def mangle(self, s):
    """Mangle a string into an Onestop component."""
    s = s.lower()
    for a,b in REPLACE_CHAR:
      s = a.sub(b,s)
    return s    

  # Entity geometry.
  def geohash(self, cache=True):
    """Return the geohash for this entity."""
    # Cache...
    if cache and 'geohash' in self.data:
      return self.data.get('geohash')
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
  def from_gtfs(cls, feed):
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
    skip = ['identifiers', 'features']
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
    # Merge identifiers.
    data['tags'] = self.merge_identifiers()
    return data

  # Tags and identifiers
  def tags(self):
    return self.data.get('tags') or {}

  def add_identifier(self, identifier, tags):
    """Add GTFS data to the set of identifiers."""
    if identifier in [i['identifier'] for i in self.identifiers]:
      raise errors.OnestopExistingIdentifier(
        "Identifier already present: %s"%identifier
      )
    self.identifiers.append({
      'identifier': identifier,
      'tags': tags
    })
  
  # Rename
  def merge(self, item):
    """Merge data into identifiers."""
    for i in item.identifiers:
      self.add_identifier(identifier=i['identifier'], tags=i['tags'])

  def merge_identifiers(self):
    tags = {}
    for i in sorted(self.identifiers, key=lambda x:x['identifier']):
      tags.update(i['tags'])
    return tags

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


class OnestopFeed(OnestopEntity):
  """Read and write Onestop Feeds."""
  onestop_type = 'f'

  def url(self):
    return self.data.get('url')
  
  def sha1(self):
    return self.data.get('sha1')
    
  def feedFormat(self):
    return self.data.get('feedFormat', 'gtfs')

  # Download the latest feed.
  def download(self, filename, debug=False):
    """Download the GTFS feed to a file."""
    util.download(self.url(), filename, sha1=self.sha1(), debug=debug)

  # Load / dump
  @classmethod
  def from_gtfs(cls, feed, feedid='f-0-unknown', **kw):
    # Create feed
    kw['sha1'] = util.sha1file(feed.filename)
    kw['geohash'] = geom.geohash_features(feed.stops())
    onestopfeed = cls(**kw)
    # Load and display information about agencies
    for agency in feed.agencies():
      agency.preload()
      oagency = OnestopOperator.from_gtfs(agency, feedid=feedid)
      onestopfeed.add_child(oagency)
    return onestopfeed
  
  def json(self):
    return {
      "onestopId": self.onestop(),
      "name": self.name(),
      "url": self.url(),
      "sha1": self.sha1(),
      "feedFormat": self.feedFormat(),
      "tags": self.tags(),
      "operatorsInFeed": [
        {
          'onestopId': i.onestop(),
          'gtfsAgencyId': i.mangle(i.name())
        }
        for i in self.operators()
      ]
    }

  # Graph
  def operatorsInFeed(self):
    return [i.onestop() for i in self.operators()]

  def operators(self):
    return set(self.children) # copy
  
  def operator(self, onestopId):
    """Return a single operator by Onestop ID."""
    return mzgtfs.util.filtfirst(self.operators(), onestop=onestopId)
  
  def routes(self):
    routes = set()
    for i in self.operators():
      routes |= i.routes()
    return routes

  def route(self, onestopId):
    """Return a single route by Onestop ID."""
    return mzgtfs.util.filtfirst(self.routes(), onestop=onestopId)
  
  def stops(self):
    stops = set()
    for i in self.operators():
      stops |= i.stops()
    return stops

  def stop(self, onestopId):
    """Return a single stop by Onestop ID."""
    return mzgtfs.util.filtfirst(self.stops(), onestop=onestopId)

class OnestopOperator(OnestopEntity):
  """Onestop Operator."""
  onestop_type = 'o'
  
  def geohash(self):
    return geom.geohash_features(self.stops())
    
  # Load / dump
  @classmethod
  def from_gtfs(cls, gtfs_agency, feedid='f-0-unknown'):
    """Load Onestop Operator from a GTFS Agency."""
    route_counter = collections.defaultdict(int)
    agency = cls(
      name=gtfs_agency.name(),
      geometry=gtfs_agency.geometry()
    )
    agency.add_identifier(
      gtfs_agency.feedid(feedid), 
      gtfs_agency.data._asdict()
    )
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
      stops[key].add_identifier(i.feedid(feedid), i.data._asdict())
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
        route_counter[key] += 1
        route.data['name'] = '%s~%s'%(route.data['name'], route_counter[key])
        route.data['onestop'] = None
        key = route.onestop()
        print "set key to:", key
        assert key not in routes
      route.pclink(agency, route)
      route.add_identifier(i.feedid(feedid), i.data._asdict())
      routes[key] = route
    # Return agency
    return agency

  @classmethod
  def from_json(cls, data):
    """Load Onestop Operator from GeoJSON."""
    agency = cls(**data)
    # Add stops
    stops = {}
    for feature in data['features']:
      if feature['onestopId'].startswith('s'):
        stop = OnestopStop.from_json(feature)
        stops[stop.onestop()] = stop
    # Add routes
    for feature in data['features']:
      if feature['onestopId'].startswith('r'):
        route = OnestopRoute.from_json(feature)
        # Get stop by id, add as child.
        for stop in feature['serves']:
          route.pclink(route, stops[stop])
        agency.pclink(agency, route)
    return agency

  def json(self):
    return {
      'type': 'FeatureCollection',
      'geometry': self.geometry(),      
      'properties': {},
      'name': self.name(),
      'tags': self.tags(),
      'identifiers': self.identifiers,
      'onestopId': self.onestop(),
      'serves': [i.onestop() for i in self.stops()],
      'features': [i.json() for i in self.routes() | self.stops()]
    }

  # Graph
  def routes(self):
    return self.children

  def route(self, onestopId):
    """Return a single route by Onestop ID."""
    return mzgtfs.util.filtfirst(self.routes(), onestop=onestopId)
  
  def stops(self):
    stops = set()
    for i in self.routes():
      stops |= i.stops()
    return stops  

  def stop(self, onestopId):
    """Return a single stop by Onestop ID."""
    return mzgtfs.util.filtfirst(self.stops(), onestop=onestopId)
        
class OnestopRoute(OnestopEntity):
  onestop_type = 'r'
  
  def geohash(self):
    """Return 10 characters of geohash."""
    return geom.geohash_features(self.stops())

  # Load / dump
  def json(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self.tags(),
      'identifiers': self.identifiers,
      'operatedBy': [i.onestop() for i in self.operators()][0],
      'serves': [i.onestop() for i in self.stops()],
    }
  
  # Graph
  def operators(self):
    return set(self.parents) # copy

  def operator(self, onestopId):
    """Return a single operator by Onestop ID."""
    return mzgtfs.util.filtfirst(self.operators(), onestop=onestopId)

  def stops(self):
    return set(self.children) # copy

  def stop(self, onestopId):
    """Return a single stop by Onestop ID."""
    return mzgtfs.util.filtfirst(self.stops(), onestop=onestopId)


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

  # Work with other interfaces
  def point(self):
    return self.geometry()['coordinates']

  # Load / dump
  def json(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self.tags(),
      'identifiers': self.identifiers,
      'servedBy': [i.onestop() for i in self.operators()],
    }

  # Graph
  def operators(self):
    agencies = set()
    for i in self.parents:
      agencies |= i.parents
    return agencies

  def operator(self, onestopId):
    """Return a single operator by Onestop ID."""
    return mzgtfs.util.filtfirst(self.operators(), onestop=onestopId)

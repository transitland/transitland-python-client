"""Operator Entity."""
import collections

import geom
import util
import errors
from entity import Entity
from stop import Stop
from route import Route

def sorted_onestop(entities):
  return sorted(entities, key=lambda x:x.onestop())

class Operator(Entity):
  """Transitland Operator Entity."""
  onestop_type = 'o'
  
  def geohash(self):
    return geom.geohash_features(self.stops())

  def _cache_onestop(self):
    key = 'onestopId'
    self.data[key] = self.make_onestop()
    for i in self.routes():
      i.data[key] = i.make_onestop()
    for i in self.stops():
      i.data[key] = i.make_onestop()
    
  # Load / dump
  @classmethod
  def from_gtfs(cls, gtfs_agency, feedid='f-0-unknown', debug=False):
    """Create Operator from a GTFS Agency."""
    route_counter = collections.defaultdict(int)
    agency = cls(
      name=gtfs_agency.name(),
      geometry=gtfs_agency.geometry()
    )
    agency.add_identifier(gtfs_agency.feedid(feedid))
    agency.add_tags(gtfs_agency.data._asdict())
    # Group stops
    stops = {}
    for i in gtfs_agency.stops():
      stop = Stop(
        name=i.name(), 
        geometry=i.geometry()
      )
      key = stop.onestop()
      if key not in stops:
        stops[key] = stop
      # Hack to maintain ref to stop
      i._tl_parent = stops[key]
      stops[key].add_identifier(i.feedid(feedid))
      stops[key].add_tags(i.data._asdict())
    # Routes
    routes = {}
    for i in gtfs_agency.routes():
      route = Route(
        name=i.name(),
        geometry=i.geometry()
      )
      if not i.stops():
        if debug: # pragma: no cover
          print "Yikes! No stops! Skipping this route." # pragma: no cover
        continue
      for j in i.stops():
        route.pclink(route, j._tl_parent)
      key = route.onestop()
      if key in routes:
        if debug: # pragma: no cover
          print "Route already exists, setting temp fix..."
        route_counter[key] += 1
        route.data['name'] = '%s~%s'%(route.data['name'], route_counter[key])
        route.data['onestop'] = None
        key = route.onestop()
        if debug: # pragma: no cover
          print "set key to:", key
        assert key not in routes
      route.pclink(agency, route)
      route.add_identifier(i.feedid(feedid))
      route.add_tags(i.data._asdict())
      routes[key] = route
    # Return agency
    return agency

  @classmethod
  def from_json(cls, data):
    """Load Operator from GeoJSON."""
    agency = cls(**data)
    # Add stops
    stops = {}
    for feature in data['features']:
      if feature['onestopId'].startswith('s'):
        stop = Stop.from_json(feature)
        stops[stop.onestop()] = stop
    # Add routes
    for feature in data['features']:
      if feature['onestopId'].startswith('r'):
        route = Route.from_json(feature)
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
      'onestopId': self.onestop(),
      'identifiers': sorted(self.identifiers()),
      'serves': sorted(self.serves()),
      'features': [
        i.json() for i in sorted_onestop(self.routes() | self.stops())
      ]
    }

  # Graph
  def serves(self):
    ret = set([i.onestop() for i in self.stops()])
    ret |= set(self.data.get('serves', []))
    return ret
    
  def routes(self):
    return set(self.children)

  def route(self, onestop_id):
    """Return a single route by Onestop ID."""
    return util.filtfirst(self.routes(), onestop=onestop_id)
  
  def stops(self):
    stops = set()
    for i in self.routes():
      stops |= i.stops()
    return stops  

  def stop(self, onestop_id):
    """Return a single stop by Onestop ID."""
    return util.filtfirst(self.stops(), onestop=onestop_id)
  
"""Operator Entity."""
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
    self.data[key] = self.data.get(key) or self.make_onestop()
    for i in self.routes():
      i.data[key] = i.data.get(key) or i.make_onestop()
    for i in self.stops():
      i.data[key] = i.data.get(key) or i.make_onestop()

  def add_tags_gtfs(self, gtfs_entity):
    keys = [
      'agency_timezone',
      'agency_url',
      'agency_phone',
      'agency_lang',
      'agency_fare_url'
    ]
    tags = gtfs_entity.data._asdict()
    for key in keys:
      if key in tags:
        self.set_tag(key, tags[key])
    self.set_tag('agency_id', tags.get('agency_id'))

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

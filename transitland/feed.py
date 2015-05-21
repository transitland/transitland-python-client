"""Feed Entity."""
import os

import geom
import util
import errors
from entity import Entity
from operator import Operator
from stop import Stop
from route import Route

class Feed(Entity):
  """Transitland Feed Entity."""
  onestop_type = 'f'

  # Feed methods.
  def url(self):
    return self.data.get('url')
  
  def sha1(self):
    return self.data.get('sha1')
    
  def feedFormat(self):
    return self.data.get('feedFormat', 'gtfs')
  
  # Download the latest feed.
  def verify_sha1(self, filename, sha1=None):
    """Check if a file is validly cached."""
    sha1 = sha1 or self.sha1()
    if os.path.exists(filename):
      if sha1 and util.sha1file(filename) == sha1:
        return True
    return False

  def download(self, filename, cache=True, verify=True):
    """Download the GTFS feed to a file. Return filename."""
    if cache and self.verify_sha1(filename):
      return filename
    util.download(self.url(), filename)
    if verify and not self.verify_sha1(filename):
      raise errors.InvalidChecksumError("Incorrect checksum: %s, expected %s"%(
        util.sha1file(filename),
        self.sha1()
      ))
    return filename

  # Load / dump
  @classmethod
  def from_gtfs(cls, gtfs_feed, feedid='f-0-unknown', debug=False, **kw):
    # Backwards compat.
    try:
      gtfs_feed.preload()
    except AttributeError, e:
      pass
    for agency in gtfs_feed.agencies():
      try:
        agency.preload()
      except AttributeError, e:
        pass
    
    # Create feed
    kw['sha1'] = util.sha1file(gtfs_feed.filename)
    kw['geohash'] = geom.geohash_features(gtfs_feed.stops())
    feed = cls(**kw)

    # Create TL Stops
    stops = {}
    # Sort; process all stations first.
    order = []
    order += sorted(filter(lambda x:x.location_type()==1, gtfs_feed.stops()), key=lambda x:x.id())
    order += sorted(filter(lambda x:x.location_type()!=1, gtfs_feed.stops()), key=lambda x:x.id())
    for gtfs_stop in order:
      stop = Stop(
        name=gtfs_stop.name(),
        geometry=gtfs_stop.geometry()
      )
      # Add to TL Stops
      key = stop.onestop()
      parent = gtfs_stop.get('parent_station')
      if parent:
        # merge into parent station
        stop = gtfs_feed.stop(parent)._tl
      elif key in stops:
        # merge into matching onestop id
        stop = stops[key]
      else:
        # new stop
        stops[key] = stop
      # Add identifiers and tags
      gtfs_stop._tl = stop
      stop.add_identifier(gtfs_stop.feedid(feedid))
      stop.add_tags(gtfs_stop.data._asdict())
    
    # Create TL Routes
    routes = {}
    for gtfs_route in gtfs_feed.routes():
      if not gtfs_route.stops():
        print "No stops:", gtfs_route.name()
        continue
      route = Route(
        name=gtfs_route.name(),
        geometry=gtfs_route.geometry()
      )
      # Link to TL Stops
      for gtfs_stop in gtfs_route.stops():
        route.add_child(gtfs_stop._tl)
      # Cache
      key = route.onestop()
      if key not in routes:
        routes[key] = route
      else:
        route = routes[key]
        print "merging route...", route, route.identifiers()
      # Maintain reference to GTFS Route
      gtfs_route._tl = route
      route.add_identifier(gtfs_route.feedid(feedid))
      route.add_tags(gtfs_route.data._asdict())
        
    for gtfs_agency in gtfs_feed.agencies():
      agency = Operator(
        name=gtfs_agency.name(),
        geometry=gtfs_agency.geometry()
      )
      agency.add_identifier(gtfs_agency.feedid(feedid))
      agency.add_tags(gtfs_agency.data._asdict())      
      for gtfs_route in gtfs_agency.routes():
        r = getattr(gtfs_route, '_tl', None)
        if not r:
          continue
        agency.add_child(r)
      feed.add_child(agency)
    return feed
    
  def json(self):
    return {
      "onestopId": self.onestop(),
      "name": self.name(),
      "url": self.url(),
      "sha1": self.sha1(),
      "feedFormat": self.feedFormat(),
      "tags": self.tags(),
      "operatorsInFeed": sorted(self.operatorsInFeed())
    }
  
  def geohash(self):
    return geom.geohash_features(self.stops())
  
  # Graph
  def operatorsInFeed(self):
    ret = set([i.onestop() for i in self.operators()])
    ret |= set(self.data.get('operatorsInFeed', []))
    return ret

  def operators(self):
    return set(self.children) # copy
  
  def operator(self, onestop_id):
    """Return a single operator by Onestop ID."""
    return util.filtfirst(self.operators(), onestop=onestop_id)
  
  def routes(self):
    routes = set()
    for i in self.operators():
      routes |= i.routes()
    return routes

  def route(self, onestop_id):
    """Return a single route by Onestop ID."""
    return util.filtfirst(self.routes(), onestop=onestop_id)
  
  def stops(self):
    stops = set()
    for i in self.operators():
      stops |= i.stops()
    return stops

  def stop(self, onestop_id):
    """Return a single stop by Onestop ID."""
    return util.filtfirst(self.stops(), onestop=onestop_id)

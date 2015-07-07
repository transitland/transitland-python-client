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

  def feedFormat(self):
    return self.data.get('feedFormat', 'gtfs')

  # Download the latest feed.
  def verify_sha1(self, filename, sha1):
    """Check if a file is validly cached."""
    if os.path.exists(filename):
      if sha1 and util.sha1file(filename) == sha1:
        return True
    return False

  def download(self, filename=None, cache=True, verify=True, sha1=None):
    """Download the GTFS feed to a file. Return filename."""
    if cache and self.verify_sha1(filename, sha1):
      return filename
    filename = util.download(self.url(), filename)
    if verify and sha1 and not self.verify_sha1(filename, sha1):
      raise errors.InvalidChecksumError("Incorrect checksum: %s, expected %s"%(
        util.sha1file(filename),
        sha1
      ))
    return filename

  # Load / dump
  def load_gtfs(self, *args, **kwargs):
    return self.bootstrap_gtfs(*args, **kwargs)

  def bootstrap_gtfs(self, gtfs_feed, feedname='unknown', populate=True):
    # Make sure the GTFS feed is completely loaded.
    gtfs_feed.preload()

    # Set onestopId
    if 'onestopId' not in self.data:
      self.data['onestopId'] = self.make_onestop(
        geohash=geom.geohash_features(gtfs_feed.stops()),
        name=feedname
      )
    feedid = self.onestop()

    # Override operator Onestop IDs
    agency_onestop = {}
    for i in self.operatorsInFeed():
      agency_onestop[i['gtfsAgencyId']] = i['onestopId']

    # Check for agencies.
    gtfs_agencies = []
    for gtfs_agency in gtfs_feed.agencies():
      if populate or gtfs_agency.id() in agency_onestop:
        gtfs_agencies.append(gtfs_agency)
      else:
        # Unknown agency
        pass
    if not gtfs_agencies:
      return

    # Create TL Stops
    stops = {}
    # sort; process all parent stations first.
    order = []
    order += sorted(filter(lambda x:x.location_type()==1, gtfs_feed.stops()), key=lambda x:x.id())
    order += sorted(filter(lambda x:x.location_type()!=1, gtfs_feed.stops()), key=lambda x:x.id())
    for gtfs_stop in order:
      # Create stop from GTFS
      stop = Stop.from_gtfs(gtfs_stop, feedid)
      # Merge into parent station
      parent = gtfs_stop.get('parent_station')
      if parent:
        stop = gtfs_feed.stop(parent)._tl_ref
      # Merge with existing stop
      key = stop.onestop()
      stop = stops.get(key) or stop
      stops[key] = stop
      # Add identifiers and tags
      gtfs_stop._tl_ref = stop
      stop.add_identifier(gtfs_stop.feedid(feedid))

    # Create TL Routes
    for gtfs_route in gtfs_feed.routes():
      if not gtfs_route.stops():
        continue
      # Create route from GTFS
      route = Route.from_gtfs(gtfs_route, feedid)
      # Link to TL Stops
      for gtfs_stop in gtfs_route.stops():
        t = getattr(gtfs_stop, '_tl_ref', None)
        if t:
          route.add_child(t)
      # Maintain reference to GTFS Route
      gtfs_route._tl_ref = route

    # Create TL Agencies
    for gtfs_agency in gtfs_agencies:
      operator = Operator.from_gtfs(
        gtfs_agency,
        feedid,
        onestop_id=agency_onestop.get(gtfs_agency.id())
      )
      for gtfs_route in gtfs_agency.routes():
        t = getattr(gtfs_route, '_tl_ref', None)
        if t:
          operator.add_child(t)
      # Inelegant.
      operator._cache_onestop()
      # Add agency to feed
      self.add_child(operator)

  def json(self):
    return {
      "onestopId": self.onestop(),
      "url": self.url(),
      "feedFormat": self.feedFormat(),
      "tags": self.tags(),
      "operatorsInFeed": self.operatorsInFeed()
    }

  def geohash(self):
    return geom.geohash_features(self.stops())

  # Graph
  def operatorsInFeed(self):
    ret = {}
    for operator in self.data.get('operatorsInFeed', []):
      ret[operator['onestopId']] = operator
    for operator in self.operators():
      data = ret.get(operator.onestop(), {})
      identifiers = set(data.get('identifiers') or [])
      # identifiers |= set(operator.identifiers())
      data['identifiers'] = sorted(identifiers)
      data['onestopId'] = operator.onestop()
      data['gtfsAgencyId'] = operator.tag('agency_id')
      ret[operator.onestop()] = data
    return sorted(ret.values(), key=lambda x:x.get('onestopId'))

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

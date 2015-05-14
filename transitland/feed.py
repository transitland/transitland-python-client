"""Feed Entity."""
import os

import geom
import util
import errors
from entity import Entity
from operator import Operator

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
      raise errors.InvalidChecksumError("Incorrect SHA1 Checksum: %s, expected %s"%(
        util.sha1file(filename),
        self.sha1()
      ))
    return filename

  # Load / dump
  @classmethod
  def from_gtfs(cls, gtfsfeed, feedid='f-0-unknown', debug=False, **kw):
    gtfsfeed.preload()
    # Create feed
    kw['sha1'] = util.sha1file(gtfsfeed.filename)
    kw['geohash'] = geom.geohash_features(gtfsfeed.stops())
    feed = cls(**kw)
    # Load and display information about agencies
    for agency in gtfsfeed.agencies():
      oagency = Operator.from_gtfs(agency, feedid=feedid, debug=debug)
      feed.add_child(oagency)
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

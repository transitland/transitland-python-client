"""Stop Entity."""
import mzgeohash

import geom
import util
import errors
from entity import Entity

class Stop(Entity):
  """Transitland Stop Entity."""
  onestop_type = 's'

  def geohash(self):
    """Return 10 characters of geohash."""
    return mzgeohash.encode(self.point())

  # Work with other interfaces
  def point(self):
    return self.geometry()['coordinates']

  def add_tags_gtfs(self, gtfs_entity):
    keys = [
      'stop_timezone',
      'wheelchair_boarding',
      'stop_desc',
      'stop_url',
      'zone_id'
    ]
    tags = gtfs_entity.data._asdict()
    for key in keys:
      if key in tags:
        self.set_tag(key, tags[key])

  # Load / dump
  def json(self):
    return {
      'type': 'Feature',
      'properties': {},
      'geometry': self.geometry(),
      'onestopId': self.onestop(),
      'name': self.name(),
      'tags': self.tags(),
      'identifiers': sorted(self.identifiers()),
      'servedBy': sorted(self.servedBy()),
    }

  # Graph
  def servedBy(self):
    """Return the operators serving this stop."""
    ret = set([i.onestop() for i in self.operators()])
    ret |= set(self.data.get('servedBy', []))
    return ret

  def operators(self):
    agencies = set()
    for i in self.parents:
      agencies |= i.parents
    return agencies

  def operator(self, onestop_id):
    """Return a single operator by Onestop ID."""
    return util.filtfirst(self.operators(), onestop=onestop_id)

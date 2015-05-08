"""Route Entity."""
import geom
import util
import errors
from entity import Entity

class Route(Entity):
  """Transitland Route Entity."""
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
      'operatedBy': self.operatedBy(),
      'identifiers': sorted(self.identifiers()),
      'serves': sorted(self.serves()),
    }

  # Graph
  def serves(self):
    ret = set([i.onestop() for i in self.stops()])
    ret |= set(self.data.get('serves', []))
    return ret

  def operatedBy(self):
    """Return the first operator."""
    ret = set(i.onestop() for i in self.operators())
    ret |= set(self.data.get('operatedBy', []))
    return sorted(ret)[0]
  
  def operators(self):
    return set(self.parents) # copy

  def operator(self, onestop_id):
    """Return a single operator by Onestop ID."""
    return util.filtfirst(self.operators(), onestop=onestop_id)

  def stops(self):
    return set(self.children) # copy

  def stop(self, onestop_id):
    """Return a single stop by Onestop ID."""
    return util.filtfirst(self.stops(), onestop=onestop_id)

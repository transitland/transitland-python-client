"""Stop Bins."""
import util
import errors
import registry
import entities

class StopBin(object):
  def __init__(self, prefix):
    self.prefix = prefix
    self._stops = {}
    
  def stops(self):
    return self._stops.values()
    
  def add_stop(self, stop):
    key = stop.onestop()
    # New stop
    if key not in self._stops:
      self._stops[key] = stop
    else:
      self._stops[key].merge(stop)

  @classmethod
  def from_json(cls, data):
    stopbin = cls(prefix=data['prefix'])    
    for feature in data['features']:
      stop = entities.OnestopStop.from_json(feature)
      stopbin.add_stop(stop)
    return stopbin
    
  def json(self):
    return {
      'type': 'FeatureCollection',
      'properties': {},
      'prefix': self.prefix,
      'features': [
        i.json() 
        for i in 
        sorted(self.stops(), key=lambda x:x.onestop())
      ]
    }    

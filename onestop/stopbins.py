import argparse
import sys
import os
import json

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
      return
    # Catch existing identifiers
    try:
      self._stops[key].merge(stop)
    except errors.OnestopExistingIdentifier:
      pass

  @classmethod
  def from_json(cls, filename):
    with open(filename) as f:
      data = json.load(f)
    stopbin = cls(prefix=data['prefix'])
    for feature in data['features']:
      stop = entities.OnestopStop(feature)
      stopbin.add_stop(stop)
    return stopbin
    
  def json(self):
    return {
      'type': 'FeatureCollection',
      'properties': {},
      'prefix': self.prefix,
      'features': [i.json() for i in self.stops()]
    }    

if __name__ == "__main__":  
  parser = argparse.ArgumentParser(description='Bin Onestop Stops by geohash')
  parser.add_argument('operators', nargs='*', help='Operator IDs')
  parser.add_argument('--onestop', help='Onestop Registry path', default='.')
  parser.add_argument('--length', 
    dest='prefixlen',
    help='Geohash prefix length', 
    type=int,
    default=5)
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()

  r = registry.OnestopRegistry(path=args.onestop)
  operators = args.operators or r.operators()
  for o in operators:
    stopbins = {}
    operator = r.operator(o)
    for stop in operator.stops():
      prefix = stop.geohash()[:args.prefixlen]
      assert len(prefix) == args.prefixlen
      # Load StopBins if exists.
      filename = os.path.join(args.onestop, 'stops', 's-%s.geojson'%prefix)
      if prefix in stopbins:
        print "Already loaded stopbin:", prefix
        stopbin = stopbins[prefix]
      elif os.path.exists(filename):
        print "Loading StopBins from GeoJSON:", prefix
        stopbin = StopBin.from_json(filename)
        stopbins[prefix] = stopbin
        print " ... %s stops"%len(stopbin._stops)
      else:
        print "Creating new StopBins:", prefix
        stopbin = StopBin(prefix)
        stopbins[prefix] = stopbin

      # Merge the Stop into StopBins.
      stopbin.add_stop(stop)

    print "Agency summary: %s"%operator.name()
    print "  Stops:", len(operator.stops())
    print "  Bins:", len(stopbins)
    
    # Write output      
    for stopbin in stopbins.values():
      filename = os.path.join(
        args.onestop, 
        'stops', 
        's-%s.geojson'%stopbin.prefix
        )
      print "Writing out StopBin:", stopbin.prefix, len(stopbin.stops())
      data = stopbin.json()
      with open(filename, 'wb') as f:
        util.json_dump_pretty(data, f)

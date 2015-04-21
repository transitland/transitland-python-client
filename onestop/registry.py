"""Read and write Onestop data."""
import sys
import os
import glob
import json
import argparse
import urllib

import mzgeohash

import util
import entities
import stopbins
import errors

class OnestopRegistry(object):
  """Onestop Registry."""
  def __init__(self, path='.'):
    """Path to directory containing 'feeds', 'operators', etc."""
    # Path to registry
    self.path = path
    if not os.path.exists(os.path.join(self.path, 'feeds')):
      raise errors.OnestopInvalidRegistry(
        'Invalid Onestop Registry directory: %s'%self.path
      )

  def _registered(self, path, prefix):
    return [
        os.path.basename(i).partition('.')[0] 
        for i in glob.glob(
          os.path.join(self.path, path, '%s-*.*json'%prefix)
        )
      ]

  def feeds(self):
    return self._registered('feeds', 'f')
          
  def feed(self, onestopId, operators=False):
    """Load a feed by onestopId."""
    filename = os.path.join(self.path, 'feeds', '%s.json'%onestopId)
    with open(filename) as f:
      data = json.load(f)    
    feed = entities.OnestopFeed.from_json(data)
    if operators:
      for i in data['operatorsInFeed']:
        operator = self.operator(i['onestopId'])
        feed.add_child(operator)
    return feed

  def operators(self):
    return self._registered('operators', 'o')

  def operator(self, onestopId):
    filename = os.path.join(self.path, 'operators', '%s.geojson'%onestopId)
    with open(filename) as f:
      data = json.load(f)
    return entities.OnestopOperator.from_json(data)
    
  def add_operator(self, operator):
    raise NotImplementedError

  def stopbin(self, geohash):
    geohash = geohash[:5]
    filename = os.path.join(self.path, 'stops', 's-%s.geojson'%geohash)
    if not os.path.exists(filename):
      return stopbins.StopBin(geohash)
    with open(filename) as f:
      data = json.load(f)
    return stopbins.StopBin.from_json(data)
  
  def stopbins(self, geohash=None, neighbors=False):
    r = self._registered('stops', 's')
    if not geohash:
      return r
    searchkeys = set()
    if geohash and neighbors:
      searchkeys |= set(mzgeohash.neighbors(geohash).values())
    elif geohash:
      searchkeys.add(geohash)
    # All against all comparison?
    ret = set()
    for stopbin in r:
      for searchkey in searchkeys:
        if stopbin.startswith('s-%s'%searchkey):
          ret.add(stopbin)
    return ret
    
  def add_stopbin(self, stop):
    stopbin = self.stopbin(stop.geohash())
    stopbin.add_stop(stop)
    filename = os.path.join(self.path, 'stops', 's-%s.geojson'%stopbin.prefix)
    data = stopbin.json()
    with open(filename, 'w') as f:
      util.json_dump_pretty(data, f)
      
      
      
      
      
      
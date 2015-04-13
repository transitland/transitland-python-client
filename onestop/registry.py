"""Read and write Onestop data."""
import sys
import os
import glob
import json
import argparse
import urllib

import entities
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
          
  def feed(self, onestopId):
    """Load a feed by onestopId."""
    filename = os.path.join(self.path, 'feeds', '%s.json'%onestopId)
    with open(filename) as f:
      data = json.load(f)    
    return entities.OnestopFeed.from_json(data)

  def operators(self):
    return self._registered('operators', 'o')

  def operator(self, onestopId):
    filename = os.path.join(self.path, 'operators', '%s.geojson'%onestopId)
    with open(filename) as f:
      data = json.load(f)
    return entities.OnestopOperator.from_json(data)

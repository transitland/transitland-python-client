"""Read and write Onestop data."""
import sys
import os
import glob
import json
import argparse
import urllib

import entities

class OnestopRegistry(object):
  """Onestop Registry."""
  def __init__(self, path=None):
    """Path to directory containing 'feeds', 'operators', etc."""
    # Path to registry
    self.path = path

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
    return OnestopFeed.from_json(
      os.path.join(self.path, 'feeds', '%s.json'%onestopId)
    )

  def operators(self):
    return self._registered('operators', 'o')

  def operator(self, onestopId):
    return entities.OnestopOperator.from_json(
      os.path.join(self.path, 'operators', '%s.geojson'%onestopId)
    )

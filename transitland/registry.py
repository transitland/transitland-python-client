"""Read and write Transitland Feed Registry."""
import sys
import os
import glob
import json
import argparse
import urllib

import mzgeohash

import util
import entities
import errors

class FeedRegistry(object):
  """Transitland Feed Registry."""
  def __init__(self, path=None):
    """Path to directory containing feeds."""
    # Path to registry
    self.path = path or os.getenv('TRANSITLAND_FEED_REGISTRY_PATH') or '.'
    if not os.path.exists(os.path.join(self.path, 'feeds')):
      raise errors.InvalidFeedRegistryError(
        'Invalid Feed Registry directory: %s'%self.path
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
    """Load a feed by Onestop ID."""
    filename = os.path.join(self.path, 'feeds', '%s.json'%onestopId)
    with open(filename) as f:
      data = json.load(f)    
    return entities.Feed.from_json(data)

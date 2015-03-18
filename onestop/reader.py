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
  
  def list_feeds(self):
    for feed in self.load_feeds():
      yield feed['onestopId']

  def load_feeds(self):
    """Load all feeds."""
    for filename in glob.glob(os.path.join(self.path, 'feeds', 'f-*.json')):
      yield OnestopFeed.load(filename)

  def load_feed(self, onestopId):
    """Load a feed by onestopId."""
    return OnestopFeed.load(
      os.path.join(self.path, 'feeds', '%s.json'%onestopId)
    )

  def operators(self):
    for filename in glob.glob(os.path.join(self.path, 'operators', 'o-*.geojson')):
      yield entities.OnestopAgency.load(filename)
    
  def operator(self, onestopId):
    return entities.OnestopAgency.load(
      os.path.join(self.path, 'feeds', '%s.geojson'%onestopId)
    )

class OnestopFeed(object):
  """Read and write Onestop Feeds."""
  def __init__(self, data=None):
    """data is the JSON data."""
    # JSON data.
    self.data = data or {}
  
  def __getitem__(self, key, default=None):
    return self.data.get(key, default)
  
  def __getattr__(self, key):
    try:
      return self.data[key]
    except:
      raise AttributeError(key)
  
  def validate(self):
    """Validate Onestop Feed."""
    pass
  
  @classmethod
  def load(cls, filename):
    """Load a Onestop Feed by filename."""
    assert os.path.exists(filename), "Filename does not exist: %s"%filename
    with open(filename) as f:
      return cls(data=json.load(f))
    
  def dump(self, filename, overwrite=False):
    """Write Onestop Feed to file."""
    if os.path.exists(filename) and not overwrite:
      raise IOError("File exists, use overwrite to ignore: %s"%filename)
    with open(filename, 'wb') as f:
      json.dump(self.data, f)
  
  def fetch(self, filename):
    """Download the GTFS feed to a file."""
    urllib.urlretrieve(self.url, filename)

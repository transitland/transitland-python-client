"""onestop-id-python-client unit tests."""
import unittest
import tempfile
import zipfile
import glob
import os
import json

import registry
import util

class TestOnestopRegistry(unittest.TestCase):
  def setUp(self):
    self.path = util.example_registry()
    self.test_feed = 'f-9qs-dta'

  def test_init(self):
    r = registry.OnestopRegistry(self.path)
    assert r.path == self.path

  def test_feeds(self):
    r = registry.OnestopRegistry(self.path)
    files = glob.glob(os.path.join(self.path, 'feeds', 'f-*.json'))
    feeds = list(r.feeds())
    assert len(files) == len(feeds)
    
  def test_feed(self):
    r = registry.OnestopRegistry(self.path)
    feed = r.feed(self.test_feed)
    assert feed
    assert feed.onestop() == self.test_feed

"""Registry unit tests."""
import unittest
import tempfile
import zipfile
import glob
import os
import json

import errors
import registry
import util

class TestFeedRegistry(unittest.TestCase):
  def setUp(self):
    self.path = util.example_registry()
    self.test_feed = 'f-9qs-dta'
    self.test_operator = 'o-9qs-demotransitauthority'

  def test_init(self):
    r = registry.FeedRegistry(self.path)
    assert r.path == self.path
    
  def test_init_check_path(self):
    with self.assertRaises(errors.InvalidFeedRegistryError):
      r = registry.FeedRegistry('/dev/null')

  def test_feeds(self):
    r = registry.FeedRegistry(self.path)
    files = glob.glob(os.path.join(self.path, 'feeds', 'f-*.json'))
    feeds = list(r.feeds())
    assert len(feeds) == len(files)
    
  def test_feed(self):
    r = registry.FeedRegistry(self.path)
    feed = r.feed(self.test_feed)
    assert feed
    assert feed.onestop() == self.test_feed

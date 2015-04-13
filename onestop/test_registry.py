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

class TestOnestopRegistry(unittest.TestCase):
  def setUp(self):
    self.path = util.example_registry()
    self.test_feed = 'f-9qs-dta'
    self.test_operator = 'o-9qs-demotransitauthority'

  def test_init(self):
    r = registry.OnestopRegistry(self.path)
    assert r.path == self.path
    
  def test_init_check_path(self):
    with self.assertRaises(errors.OnestopInvalidRegistry):
      r = registry.OnestopRegistry('/dev/null')

  def test_feeds(self):
    r = registry.OnestopRegistry(self.path)
    files = glob.glob(os.path.join(self.path, 'feeds', 'f-*.json'))
    feeds = list(r.feeds())
    assert len(feeds) == len(files)
    
  def test_feed(self):
    r = registry.OnestopRegistry(self.path)
    feed = r.feed(self.test_feed)
    assert feed
    assert feed.onestop() == self.test_feed

  def test_operators(self):
    r = registry.OnestopRegistry(self.path)
    operators = r.operators()
    files = glob.glob(os.path.join(self.path, 'feeds', 'f-*.json'))
    assert len(operators) == len(files)
    
  def test_operator(self):
    r = registry.OnestopRegistry(self.path)
    operator = r.operator(self.test_operator)
    assert operator.onestop() == self.test_operator

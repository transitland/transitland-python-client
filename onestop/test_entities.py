"""Entity tests."""
import os
import unittest
import sys
import pprint

import mzgtfs.feed

import util
import entities

def operator_from_feed(*args, **kw):
  return mzgtfs.feed.Feed(util.example_feed(*args, **kw))

class TestOnestopEntity(unittest.TestCase):
  pass

class TestOnestopFeed(unittest.TestCase):
  def test_from_gtfs(self):
    feed = operator_from_feed()
    onestopfeed = entities.OnestopFeed.from_gtfs(
      feed,
      name='test'
      )
    assert onestopfeed.name() == 'test'
    assert onestopfeed.onestop() == 'f-9qs-test'

class TestOnestopOperator(unittest.TestCase):
  def test_init(self):
    entity = entities.OnestopOperator()
    

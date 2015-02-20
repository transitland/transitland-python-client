"""onestop-id-python-client unit tests."""
import unittest
import tempfile
import zipfile
import glob
import os
import json

import onestop

TEST_FEED = {
  "onestopId": "f-9q8y-SFMTA",
  "url": "http://archives.sfmta.com/transitdata/google_transit.zip",
  "feedFormat": "gtfs",
  "tags": {
    "licenseUrl": "http://www.sfmta.com/about-sfmta/reports/gtfs-transit-data"
  },
  "operatorsInFeed": [
    {
      "onestopId": "o-9q8y-SFMTA",
      "gtfsAgencyId": "SFMTA"
    }
  ]
}

class TestOnestopRegistry(unittest.TestCase):
  def setUp(self):
    self.path = os.path.join('..', '..','onestop-id-registry')
    self.test_feed = 'f-9q8y-SFMTA'

  def test_init(self):
    registry = onestop.OnestopRegistry(self.path)
    assert registry.path == self.path

  def test_load_feeds(self):
    registry = onestop.OnestopRegistry(self.path)
    files = glob.glob(os.path.join(self.path, 'feeds', 'f-*.json'))
    feeds = list(registry.load_feeds())
    assert len(files) == len(feeds)
    
  def test_load_feed(self):
    registry = onestop.OnestopRegistry(self.path)
    feed = registry.load_feed(self.test_feed)
    assert feed
    assert feed.onestopId == self.test_feed
  
class TestOnestopFeed(unittest.TestCase):
  def setUp(self):
    self.path = os.path.join('..','..','onestop-id-registry')
    self.test_feed = 'f-9q8y-SFMTA'
  
  def test_load_filename(self):
    feed = onestop.OnestopFeed.load(os.path.join(self.path, 'feeds', '%s.json'%self.test_feed))
    assert feed
    assert feed.onestopId == self.test_feed
    
  def test_fetch(self):
    feed = onestop.OnestopFeed(data=TEST_FEED)
    tmp = tempfile.NamedTemporaryFile().name
    print "fetching to:", tmp
    feed.fetch(tmp)
    assert os.path.exists(tmp)
    assert zipfile.is_zipfile(tmp)

  def test_validate(self):
    feed = onestop.OnestopFeed(data=TEST_FEED)
    feed.validate()
  
  def test_dump(self):
    feed = onestop.OnestopFeed(data=TEST_FEED)
    tmp = tempfile.NamedTemporaryFile().name
    print "dumping to:", tmp
    feed.dump(tmp, overwrite=True)
    assert os.path.exists(tmp)
    with open(tmp) as f:
      data = json.load(f)
    assert data['onestopId'] == feed.onestopId
      
if __name__ == '__main__':
    unittest.main()
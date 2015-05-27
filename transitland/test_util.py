"""Utility unit tests."""
import tempfile
import unittest
import os
import cStringIO as StringIO

import errors
import util

class Test_download(unittest.TestCase):
  def setUp(self):
    self.url = 'file://%s'%os.path.abspath(util.example_gtfs_feed_path())    
    self.sha1_gtfs = '4e5e6a2668d12cca29c89a969d73e05e625d9596'
  
  def test_download(self):
    # Create a temporary file name, then delete it...
    # Of course, never do this in non-testing code!!
    f = tempfile.NamedTemporaryFile()
    f.close()
    # Make sure it doesn't exist.
    assert not os.path.exists(f.name)
    # Now download, using the deleted temporary file name.
    util.download(self.url, f.name)
    assert util.sha1file(f.name) == self.sha1_gtfs
    
  def test_download_nofile(self):
    filename = util.download(self.url)
    assert util.sha1file(filename) == self.sha1_gtfs

  def test_download_nourl(self):
    with self.assertRaises(ValueError):
      util.download(None)
  
class Test_json_pretty_dump(unittest.TestCase):
  def test_json_pretty_dump(self):
    f = StringIO.StringIO()
    data = {'one':'two', 'a':'b'}
    util.json_pretty_dump(data, f)
    f.seek(0)
    check = f.read()
    assert '    "a"' in check
    assert '    "one"' in check
  
class Test_sha1file(unittest.TestCase):
  def test_sha1file(self):
    data = util.sha1file(util.example_gtfs_feed_path())
    expect = '4e5e6a2668d12cca29c89a969d73e05e625d9596'
    assert data == expect
  
class Test_example_registry(unittest.TestCase):
  def test_example_registry(self):
    data = util.example_registry()
    assert os.path.isdir(data)
    assert os.path.isdir(os.path.join(data, 'feeds'))

class Test_example_feed(unittest.TestCase):
  def test_example_feed(self):
    data = util.example_gtfs_feed_path()
    assert os.path.exists(data)
    assert data.endswith('.zip')
  
  
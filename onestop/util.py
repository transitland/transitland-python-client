"""Helpful utilitors."""
import urllib
import os
import json
import hashlib

def download(url, filename, sha1=None, cache=True):
  if cache and os.path.exists(filename):
    if sha1 and sha1file(filename) == sha1:
      # Cached file, valid sha1 hash
      print "Cached: %s (valid sha1)"%(filename)
      return filename
    elif sha1:
      print "Cached, but incorrect signature."
    else:
      # Cached file, no sha1
      print "Cached: %s (sha1 not checked)"%(filename)
      return filename
  print "Downloading: %s -> %s"%(url, filename)
  urllib.urlretrieve(url, filename)
  return filename

def json_dump_pretty(data, f):
  json.dump(
    data,
    f,
    sort_keys=True,
    indent=4,
    separators=(',', ': ')
  )

def sha1file(filename, blocksize=65536):
  """Return SHA1 hash of a file."""
  h = hashlib.sha1()
  with open(filename, 'rb') as f:
      chunk = f.read(blocksize)
      while len(chunk) > 0:
          h.update(chunk)
          chunk = f.read(blocksize)
  return h.hexdigest()

def example_registry(path=None):
  return os.path.join(
    os.path.dirname(__file__), 
    'examples'    
  )

def example_feed(feed='f-9qs-dta.zip'):
  return os.path.join(
    os.path.dirname(__file__), 
    'examples',
    'data',
    feed
    )

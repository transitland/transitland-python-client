"""Helpful utilitors."""
import urllib
import os
import json
import hashlib

def download(url, filename, checksum=None):
  # filename = tempfile.NamedTemporaryFile().name  
  if os.path.exists(filename) and sha1(filename) == checksum:
    print "Cached: %s"%(filename)
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

def sha1(filename, blocksize=65536):
  """Return SHA1 Checksum of a file."""
  h = hashlib.sha1()
  with open(filename, 'rb') as f:
      chunk = f.read(blocksize)
      while len(chunk) > 0:
          h.update(chunk)
          chunk = f.read(blocksize)
  return h.hexdigest()
  
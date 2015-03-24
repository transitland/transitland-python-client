"""Helpful utilitors."""
import json
import hashlib

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
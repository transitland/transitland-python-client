"""Helpful utilitors."""
import urllib
import os
import json
import hashlib
import re

ONESTOP_LENGTH = 64
GEOHASH_LENGTH = 10

# Regexes
REPLACE_CHAR = [
  # replace &, @, and / with ~
  [r'[\-\:\&\@\/]+','~'], 
  # [r' - ','~'], 
  # replace every other special char
  [r'[^~0-9a-zA-Z]+', '']
]
REPLACE_CHAR = [[re.compile(i[0]), i[1]] for i in REPLACE_CHAR]

REPLACE_ABBR = [
  'alley',
  'avenue',
  'ave',
  'av',
  'boulevard',
  'blvd',
  'center',
  'ctr',
  'drive',
  'dr',
  'expressway',
  'expw',
  'expy',
  'freeway',
  'fwy',
  'highway',
  'hwy',
  'lane',
  'ln',
  'parkway',
  'pkwy',
  'road',
  'rd',
  'street',
  'st',
  'streets',
  'sts',
  'way'
]
REPLACE_ABBR = [[re.compile(r'\b%s\b'%i), ''] for i in REPLACE_ABBR]

# Copied from mzgtfs.util
def filtany(entities, **kw):
  """Filter a set of entities based on method return. Use keyword arguments.
  
  Example:
    filtany(entities, id='123')
    filtany(entities, name='bart')

  Multiple filters are 'OR'.
  """
  ret = set()
  for k,v in kw.items():
    for entity in entities:
      if getattr(entity, k)() == v:
        ret.add(entity)
  return ret

# Copied from mzgtfs.util
def filtfirst(entities, **kw):
  """Return the first matching entity, sorted by id()."""
  ret = sorted(filtany(entities, **kw), key=lambda x:x.id())
  if not ret:
    raise ValueError('No result')
  return ret[0]

def printf(msg):
  print msg

def download(url, filename=None):
  """Download url to filename."""
  if not url:
    raise ValueError("No url given.")
  filename, response = urllib.urlretrieve(url, filename)
  return filename

def json_pretty_dump(data):
  print json.dumps(
    data,
    sort_keys=True,
    indent=4,
    separators=(',', ': ')
  )

def json_pretty_dump(data, f):
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

def example_gtfs_feed_path(feed='f-9qs-dta.zip'):
  return os.path.join(
    os.path.dirname(__file__), 
    'examples',
    'data',
    feed
    )

def example_gtfs_feed(*args, **kw):
  import mzgtfs.feed
  a = mzgtfs.feed.Feed(
    example_gtfs_feed_path(*args, **kw)
  )
  return a

def example_feed():
  import feed
  return feed.Feed.from_gtfs(
    example_gtfs_feed(), 
    feedid='f-0-dta'
  )

def example_export():
  filename = os.path.join(
    os.path.dirname(__file__), 
    'examples',
    'dta.json'
  )
  data = {}
  with open(filename) as f:
    data = json.load(f)
  return data
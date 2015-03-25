"""Read a GTFS file and convert to Onestop JSON."""
import argparse
import json
import sys
import os

import tempfile
import urllib

import util
import registry
import entities
import mzgtfs.reader

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Onestop Registry from GTFS.')
  parser.add_argument('--filename', help='GTFS File')
  parser.add_argument('--url', help='GTFS url')
  parser.add_argument('--feedid', help='Feed ID', default='unknown')
  parser.add_argument('--onestop', help='Onestop Registry path', default='.')
  parser.add_argument(
    '--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()

  # Create dirs
  for i in ['feeds', 'operators', 'data']:
    try:
      os.makedirs(i)
    except OSError, e:
      pass
  
  # Load from registry, then update.
  carry = {}
  carry['name'] = args.feedid
  checksum = None
  try:
    r = registry.OnestopRegistry(args.onestop)
    f = r.feed('f-%s'%args.feedid)
  except IOError, e:
    pass
  else:
    carry['url'] = f.url
    carry['tags'] = f.tags
    checksum = f.sha1
    # Use previous url if no filename or url was provided.
    args.url = args.url or f.url
  
  # Download GTFS feed.
  filename = None
  if args.filename:
    filename = args.filename
  elif args.url:
    filename = util.download(
      args.url, 
      os.path.join('data', 'g-%s.zip'%args.feedid),
      checksum=checksum
    )
  else:
    raise Exception("No filename or url provided.")
  
  # Load from GTFS.
  feed = entities.OnestopFeed.from_gtfs(filename, debug=args.debug, **carry)

  # Print basic feed information.
  print "Feed:", 'f-%s'%args.feedid
  print "  Operators:", len(feed.operators())
  print "  Routes:", len(feed.routes())
  print "  Stops:", len(feed.stops())

  # Write out updated feed.
  outfile = os.path.join('feeds', 'f-%s.json'%args.feedid)
  with open(outfile, 'w') as f:
    util.json_dump_pretty(feed.json(), f)
  
  # Print basic operator information.
  for operator in feed.operators():
    print "Operator:", operator.name()
    print "  Routes:", len(operator.routes())
    print "  Stops:", len(operator.stops())
    # Write out updated operators.
    outfile = os.path.join('operators', '%s.geojson'%operator.onestop())
    with open(outfile, 'w') as f:
      util.json_dump_pretty(operator.json(), f)

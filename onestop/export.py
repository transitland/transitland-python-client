"""Read a GTFS file and convert to Onestop JSON."""
import argparse
import json
import sys
import os

import util
import registry
import entities
import mzgtfs.reader

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS to Agency')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--path', help='Onestop Registry path')
  parser.add_argument('--agencies', help='Export agencies', action='store_true')
  parser.add_argument('--feed', help='Export feed', action='store_true')
  parser.add_argument('--feedid', help='Feed ID', default='unknown')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()
  
  # todo: load from registry, then update.
  # r = registry.OnestopRegistry(args.path)
  feed = entities.OnestopFeed.from_gtfs(
    args.filename, 
    name=args.feedid
  )
  print "Feed:", feed.onestop()
  print "  Operators:", len(feed.operators())
  print "  Routes:", len(feed.routes())
  print "  Stops:", len(feed.stops())
  if args.feed:
    with open(os.path.join('feeds', '%s.json'%feed.onestop()), 'w') as f:
      util.json_dump_pretty(feed.json(), f)

  for operator in feed.operators():
    print "Operator:", operator.name()
    print "  Routes:", len(operator.routes())
    print "  Stops:", len(operator.stops())
    if args.agencies:
      with open(os.path.join('operators', '%s.geojson'%operator.onestop()), 'w') as f:
        util.json_dump_pretty(operator.json(), f)

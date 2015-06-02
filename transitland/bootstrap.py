"""Create a Transitland Feed Registry entry from a GTFS file."""
import argparse
import json
import sys
import os

import mzgtfs.feed

import geom
import util
import registry
import entities

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Create Transitland Feed Registry entry from GTFS.'
  )
  parser.add_argument('--url', help='GTFS url')
  parser.add_argument('--filename', help='GTFS feed filename')
  parser.add_argument('--feedname', help='Feed name')
  parser.add_argument(
    '--output', 
    help='Specify output JSON filename; default is <onestopId>.json'
  )
  parser.add_argument(
    '--print', 
    help='Print JSON output', 
    action='store_true', 
    dest='printjson'
  )
  parser.add_argument(
    '--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()

  if not (args.url or args.filename):
    raise Exception("Must specify either --filename or --url")

  # Download feed.
  filename = args.filename
  if args.url:
    print "Downloading: %s"%args.url
    filename = util.download(args.url)

  # Everything is now ready to create the feed.
  print "Loading feed:", filename
  f = mzgtfs.feed.Feed(filename, debug=args.debug)

  # Create Transitland Feed from GTFS.
  kw = {}
  kw['debug'] = args.debug
  kw['url'] = args.url
  if args.feedname:
    kw['feedname'] = args.feedname
  feed = entities.Feed.from_gtfs(f, **kw)
  
  # Print basic feed information.
  print "Feed:", feed.onestop()
  print "  Stops:", len(feed.stops())
  print "  Routes:", len(feed.routes())
  print "  Operators:", len(feed.operators())
  # Print basic operator information.
  for operator in feed.operators():
    print "  Operator:", operator.name()
    print "    Routes:", len(operator.routes())
    print "    Stops:", len(operator.stops())

  # Write out updated feed.
  output = args.output or '%s.json'%feed.onestop()
  data = feed.json()
  if args.printjson:
    util.json_pretty_print(data)
  if os.path.exists(output):
    print "Error: Filename %s already exists."%output
    sys.exit(1)
  else:
    print "Writing to %s"%output
    with open(output, 'w') as f:
      util.json_pretty_dump(data, f)
    


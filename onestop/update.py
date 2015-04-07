"""Read a GTFS file and convert to Onestop JSON."""
import argparse
import json
import sys
import os

import tempfile
import urllib

import mzgtfs.feed

import util
import registry
import entities

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Onestop Registry from GTFS.')
  parser.add_argument('feedids', nargs='*', help='Feed IDs')
  parser.add_argument('--all', help='Update all feeds', action='store_true')
  parser.add_argument('--url', help='GTFS url')
  parser.add_argument('--filename', help='GTFS feed filename')
  parser.add_argument('--feedname', help='Feed name, if generating from GTFS')
  parser.add_argument('--onestop', help='Onestop Registry path', default='.')
  parser.add_argument('--output', help='Output path (default: Onestop)')

  parser.add_argument(
    '--cache',
    help='Feed cache setting. Allowed: force, ignore, cache (default)',
    default='cache')
  parser.add_argument(
    '--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()

  # Create dirs
  args.output = args.output or args.onestop
  for i in ['feeds', 'operators', 'data']:
    try:
      os.makedirs(os.path.join(args.output, i))
    except OSError, e:
      pass

  # Registry
  r = registry.OnestopRegistry(args.onestop)

  # Feeds to update
  feedids = args.feedids
  if args.all:
    feedids = r.feeds()
    
  if len(feedids) == 0:
    raise Exception("No feeds specified; try --all.")
  if len(feedids) > 1 and (args.filename or args.url):
    raise Exception("Cannot specify --filename or --url with multiple feeds.")

  for feedid in feedids:
    # Load from registry, then update.
    feed = {}
    try:
      f = r.feed(feedid)
    except IOError, e:
      print "Could not load feed:", feedid
    else:
      feed['name'] = f.name()
      feed['url'] = f.url()
      feed['tags'] = f.tags()
      feed['sha1'] = f.sha1()

    # Cache settings.
    if args.cache == 'cache':
      sha1 = feed.get('sha1')
      cache = True
    elif args.cache == 'force':
      sha1 = None
      cache = True
    elif args.cache == 'ignore':
      sha1 = None
      cache = False
      
    # Download GTFS feed.
    filename = args.filename
    url = args.url or feed.get('url')
    if args.filename:
      pass
    elif url:
      filename = util.download(
        url, 
        os.path.join(args.output, 'data', '%s.zip'%feedid),
        sha1=sha1,
        cache=cache
      )
    else:
      raise Exception("No filename or url provided.")
  
    # Load from GTFS.
    print "Loading feed:", feedid
    f = mzgtfs.feed.Feed(filename)
    feed = entities.OnestopFeed.from_gtfs(
      f, 
      debug=args.debug, 
      name=feed.get('name') or args.feedname,
      url=url,
      tags=feed.get('tags')
    )

    # Print basic feed information.
    print "Feed:", feedid
    print "  Operators:", len(feed.operators())
    print "  Routes:", len(feed.routes())
    print "  Stops:", len(feed.stops())

    # Write out updated feed.
    outfile = os.path.join(args.output, 'feeds', '%s.json'%feedid)
    # do this so file isn't emptied if there's an exception...
    data = feed.json() 
    with open(outfile, 'w') as f:
      util.json_dump_pretty(data, f)
  
    # Print basic operator information.
    for operator in feed.operators():
      print "Operator:", operator.name()
      print "  Routes:", len(operator.routes())
      print "  Stops:", len(operator.stops())
      # Write out updated operators.
      outfile = os.path.join(args.output, 'operators', '%s.geojson'%operator.onestop())
      data = operator.json()
      with open(outfile, 'w') as f:
        util.json_dump_pretty(data, f)

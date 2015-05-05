"""Fetch Onestop feeds."""
import argparse
import os
import json

import mzgtfs.feed

import entities
import registry
import util
import datastore

def run():
  parser = argparse.ArgumentParser(description='Read Onestop Registry')
  parser.add_argument('feedids', nargs='*', help='Onestop Feed IDs')
  parser.add_argument('--debug', help='Debug', action='store_true')
  parser.add_argument('--onestop', help='Onestop Registry Path')
  parser.add_argument('--apitoken', 
    help='API Token',
    default=os.getenv('ONESTOP_API_AUTH_TOKEN')
  )
  parser.add_argument("--host", 
    help="Datastore Host", 
    default=os.getenv('ONESTOP_DATASTORE_HOST') or 'http://localhost:3000'
  )
  args = parser.parse_args()

  ##### Check for updated feeds #####
  print "===== Updating feeds ====="
  onestopregistry = registry.OnestopRegistry(path=args.onestop)
  feedids = args.feedids or onestopregistry.feeds()
  for feedid in feedids:
    feed = onestopregistry.feed(feedid)
    # If the feed is up-to-date, skip.
    if not feed.download(debug=args.debug):
      continue
      
    print "===== Validating feed: %s ====="%(feed.onestop())
    # run feedvalidator.py
    
    print "===== Updating datastore: %s ====="%(feed.onestop())
    onestopfeed = entities.OnestopFeed.from_gtfs(
      mzgtfs.feed.Feed(feed.filename()), 
      feedid=feed.name()
    )
    updater = datastore.Datastore(
      args.host, 
      apitoken=args.apitoken, 
      debug=args.debug
    )
    for entity in onestopfeed.operators():
      updater.update_operator(entity)

if __name__ == "__main__":
  run()

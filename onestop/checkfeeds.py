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
  parser.add_argument('--authtoken', 
    help='API Authentication Token',
    default=os.getenv('TRANSITLAND_DATASTORE_AUTH_TOKEN')
  )
  parser.add_argument("--datastore", 
    help="Datastore Datastore URL", 
    default=os.getenv('TRANSITLAND_DATASTORE_URL') or 'http://localhost:3000/api/v1'
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
    # feed.validate_feedvalidator()
    gtfsfeed = mzgtfs.feed.Feed(feed.filename())
    gtfs.preload()
    gtfsfeed.validate()
    
    print "===== Updating datastore: %s ====="%(feed.onestop())
    onestopfeed = entities.OnestopFeed.from_gtfs(
      gtfsfeed, 
      feedid=feed.name()
    )
    updater = datastore.Datastore(
      args.datastore, 
      apitoken=args.authtoken, 
      debug=args.debug
    )
    for entity in onestopfeed.operators():
      updater.update_operator(entity)
      
if __name__ == "__main__":
  run()

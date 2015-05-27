"""Export a GTFS feed as Transitland GeoJSON"""
import argparse
import mzgtfs.feed

import feed
import util

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Export a GTFS feed as Transitland GeoJSON'
  )
  parser.add_argument('filename', help='GTFS feed filename')
  parser.add_argument('--feedname', help='Feed name')
  parser.add_argument(
    '--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()
  
  gtfs_feed = mzgtfs.feed.Feed(args.filename)
  feed = feed.Feed.from_gtfs(gtfs_feed)
  for operator in feed.operators():
    print "===== Operator: %s ====="%operator.onestop()
    data = operator.json()
    util.json_pretty_dump(data)
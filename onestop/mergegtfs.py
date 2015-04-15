"""Merge Onestop IDs into a GTFS feed."""
import os
import argparse

import entities
import mzgtfs.feed

def map_onestop_gtfs(entities, key):
  rels = {}
  for entity in entities:
    for identifier in entity.identifiers:
      rels[identifier['tags'][key]] = entity.onestop()
  return rels

def assign_onestop_ids(feed, onestopfeed, feedents, onestopfeedents, key):
  rels = map_onestop_gtfs(onestopfeedents, key)
  for entity in feedents:
    entity['onestop_id'] = rels[entity[key]]

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Merge Onestop IDs into a GTFS feed.'
  )
  parser.add_argument('filename', help='Input GTFS Zip file')
  parser.add_argument('outfile', help='Output filename')
  parser.add_argument('--feedname', default='f-9q9-bayarearapidtransit')
  parser.add_argument('--debug', action='store_true')
  args = parser.parse_args()
  
  feed = mzgtfs.feed.Feed(args.filename, debug=args.debug)
  onestopfeed = entities.OnestopFeed.from_gtfs(feed, feedid=args.feedname)
  # Assign Onestop IDs for agencies, routes, and stops.
  assign_onestop_ids(
    feed, 
    onestopfeed, 
    feed.agencies(), 
    onestopfeed.operators(), 
    'agency_id'
  )
  assign_onestop_ids(
    feed, 
    onestopfeed, 
    feed.routes(), 
    onestopfeed.routes(), 
    'route_id'
  )
  assign_onestop_ids(
    feed, 
    onestopfeed, 
    feed.stops(), 
    onestopfeed.stops(), 
    'stop_id'
  )
  # Write out.
  feed.write('agency.txt', feed.agencies())
  feed.write('routes.txt', feed.routes())
  feed.write('stops.txt', feed.stops())
  feed.make_zip(args.outfile, path='.', clone=args.filename)
  for i in ['agency.txt', 'routes.txt', 'stops.txt']:
    os.unlink(i)
      
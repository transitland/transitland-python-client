"""Read a GTFS file and convert to Onestop JSON."""
import argparse
import json
import sys

import entities
import mzgtfs.reader

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS to Onestop')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--feedid', help='Feed ID', default='unknown')
  parser.add_argument('--debug', 
    help='Show helpful debugging information', 
    action='store_true')
  args = parser.parse_args()

  g = mzgtfs.reader.Reader(args.filename, feedid=args.feedid)
  for agency in g.agencies():
    agency.preload()
    oagency = entities.OnestopAgency.from_gtfs(agency)
    print "Agency:", oagency.name()
    print "  Routes:", len(oagency.routes())
    if args.debug:
      for route in oagency.routes():
        print route
    print "  Stops:", len(oagency.stops())
    if args.debug:
      for stop in oagency.stops():
        print stop

    # Export
    outfile = '%s.geojson'%oagency.onestop()
    print "Writing: %s"%outfile
    with open(outfile, 'w') as f:
      json.dump(
        oagency.geojson(), 
        f, 
        sort_keys=True, 
        indent=4, 
        separators=(',', ': ')
      )

      

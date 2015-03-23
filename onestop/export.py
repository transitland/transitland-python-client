"""Read a GTFS file and convert to Onestop JSON."""
import argparse
import json
import sys

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
  
  r = registry.OnestopRegistry(args.path)
  

  g = mzgtfs.reader.Reader(args.filename, feedid=args.feedid)
  # Load and display information about agencies
  for agency in g.agencies():
    agency.preload()
    oagency = entities.OnestopOperator.from_gtfs(agency)
    print "Operator:", oagency.name()
    print "  Routes:", len(oagency.routes())
    if args.debug:
      for route in oagency.routes():
        print route
    print "  Stops:", len(oagency.stops())
    if args.debug:
      for stop in oagency.stops():
        print stop

    # Export agency
    if args.agencies:
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

  # Print basic information about feed
  

  # print "Feed:", feedid
  # print "  Agencies:", len(g.agencies())
  # print "  Routes:", len(g.routes())
  # print "  Stops:", len(g.stops())

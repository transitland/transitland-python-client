"""Provide useful information about a GTFS file."""
import argparse

import geohash
import gtfs

def jp(data, key):
  return ", ".join(sorted(set(i.get(key).strip() for i in data)))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Information')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', help='Show helpful debugging information', action='store_true')
  args = parser.parse_args()
  g = gtfs.GTFSReader(args.filename)
  stops_centroid = g.stops_centroid()
  stops_centroid_geohash = g.stops_geohash(debug=args.debug)
  print "==== GTFS:", g.filename
  print "Required:"
  print "  Agencies:", jp(g.read('agency.txt'), 'agency_name')
  print "  Routes #:", len(g.read('routes.txt'))
  print "  Unique route_short_name:", jp(g.read('routes.txt'), 'route_short_name')
  print "  Stops #:", len(g.read('stops.txt'))
  print "  Unique stop_name:", jp(g.read('stops.txt'), 'stop_name')
  print "  Trips:", len(g.read('trips.txt'))
  print "  Stop times:", len(g.read('stop_times.txt'))
  print "  Service IDs:", len(g.read('calendar.txt'))
  print "Optional:"
  print "  Shapes?:", len(g.read('shapes.txt'))
  print "  Frequencies?:", len(g.read('frequencies.txt'))
  print "Onestop details:"
  print "  Stops centroid:", stops_centroid
  print "  Stops centroid geohash:", geohash.encode(stops_centroid)
  print "  Stops centroid geohash with all stops in neighbors:", stops_centroid_geohash

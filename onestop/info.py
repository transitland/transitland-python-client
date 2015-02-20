"""Provide useful information about a GTFS file."""
import argparse

import geohash
import gtfs

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Information')
  parser.add_argument('filename', help='GTFS File')
  parser.add_argument('--debug', help='Show helpful debugging information', action='store_true')
  args = parser.parse_args()
  g = gtfs.GTFSReader(args.filename)
  stops_centroid = g.stops_centroid()
  stops_centroid_geohash = g.stops_geohash(debug=args.debug)
  print "==== GTFS:", g.filename
  print "Stops centroid:",stops_centroid
  print "Stops centroid geohash:", geohash.encode(stops_centroid)
  print "Stops centroid geohash with all stops in neighbors:", stops_centroid_geohash

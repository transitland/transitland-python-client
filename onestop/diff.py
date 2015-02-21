"""Compare two GTFS feeds."""
import sys
import json
import collections
import argparse

import gtfs
import geohash

def strip(s):
  return str(s).strip().lower()

def add_geohash(data):
  for stop in data:
    stop['geohash'] = geohash.encode((float(stop['stop_lat']), float(stop['stop_lon'])))

class GTFSCompare(object):
  def __init__(self, filename1, filename2):
    self.g1 = gtfs.GTFSReader(filename1)
    self.g2 = gtfs.GTFSReader(filename2)
      
  def compare(self, filename, keys):
    d1 = self.g1.read(filename)
    d2 = self.g2.read(filename)
    if filename == 'stops.txt':
      add_geohash(d1)
      add_geohash(d2)
    return self.match(list(d1), list(d2), keys)
    
  def match(self, data1, data2, keys):
    matched = {}
    unmatched = {}
    new = {}
    dk1 = set([tuple(strip(i.get(k)) for k in keys) for i in data1])
    dk2 = set([tuple(strip(i.get(k)) for k in keys) for i in data2])
    found = dk1 & dk2
    lost = dk1 - dk2
    new = dk2 - dk1
    return found, lost, new

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Comparison Tool')
  parser.add_argument('filename1', help='GTFS File 1')
  parser.add_argument('filename2', help='GTFS File 2')
  parser.add_argument('--table', help='Comparison table (GTFS filename.txt)', default='routes.txt')
  parser.add_argument('--key', help='Comparison key', action="append", dest='keys')
  parser.add_argument('--display', help='Display key', default='route_long_name')
  parser.add_argument('--flip', help='Flip comparison', action='store_true')
  args = parser.parse_args()
  args.keys = args.keys or ['route_short_name']
  if args.flip:
    args.filename1, args.filename2 = args.filename2, args.filename1
  # 
  gc = GTFSCompare(args.filename1, args.filename2)
  found, lost, new = gc.compare(args.table, keys=args.keys)
  print "==== Found:", len(found), "\n", found
  print "==== Lost:", len(lost), "\n", lost
  print "==== New:", len(new), "\n", new


import sys
import csv
import zipfile
import json
import collections
import argparse

def strip(s):
  return str(s).strip().lower()
  
class GTFSReader(object):
  def __init__(self, filename):
    self.zipfile = zipfile.ZipFile(filename)

  def readcsv(self, filemame):
    with self.zipfile.open(filemame) as f:
      data = csv.DictReader(f)
      for i in data:
        yield i
    
class GTFSCompare(object):
  def __init__(self, filename1, filename2):
    self.g1 = GTFSReader(filename1)
    self.g2 = GTFSReader(filename2)
      
  def compare(self, filename, keys):
    d1 = self.g1.readcsv(filename)
    d2 = self.g2.readcsv(filename)
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
  print "found:", found
  print "lost:", lost
  print "new:", new

  # reworking...
  # Pretty formatting.
  # def printkey(k, width=40):
  #   return "\t"+", ".join(k).ljust(width)
  # width = max([len(printkey(i, width=0)) for i in matched.keys() + unmatched.keys()] or [0])
  # width += 5
  # for k,(a,b) in sorted(matched.items()):
  #   if strip(a.get(args.display)) != strip(b.get(args.display)):
  #     print printkey(k, width=width), a.get(args.display), "->", b.get(args.display)
  #   else:
  #     print printkey(k, width=width), a.get(args.display)
  # for k,a in sorted(unmatched.items()):
  #   print printkey(k, width=width), a.get(args.display), "(No Match!)"


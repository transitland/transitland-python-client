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
      
  def compare(self, filename, key, display=None):
    d1 = self.g1.readcsv(filename)
    d2 = self.g2.readcsv(filename)
    return self.match(list(d1), list(d2), key)
    
  def match(self, data1, data2, key):
    matched = {}
    unmatched = {}
    for i in data1:
      found = False
      for j in data2:
        if strip(i[key]) == strip(j[key]):
          found = True
          matched[strip(i[key])] = (i,j)
      if not found:
        unmatched[strip(i[key])] = i
    return matched, unmatched

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='GTFS Comparison Tool')
  parser.add_argument('filename1', help='GTFS File 1')
  parser.add_argument('filename2', help='GTFS File 2')
  parser.add_argument('--table', help='Comparison table (GTFS filename.txt)', default='routes.txt')
  parser.add_argument('--key', help='Comparison key', default='route_short_name')
  parser.add_argument('--display', help='Display key', default='route_long_name')
  args = parser.parse_args()
  # 
  gc = GTFSCompare(args.filename1, args.filename2)
  matched, unmatched = gc.compare(args.table, key=args.key, display=args.display)
  for k,(a,b) in matched.items():
    if strip(a.get(args.display)) != strip(b.get(args.display)):
      print k, "\t\t", a.get(args.display), "->", b.get(args.display)
    else:
      print k, "\t\t", a.get(args.display)
  for k,a in unmatched.items():
    print k, "\t\t", a.get(args.display), "(No Match!)"  


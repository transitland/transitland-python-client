"""GTFS tools."""
import zipfile
import csv

import geohash

class GTFSReader(object):
  def __init__(self, filename):
    self.cache = {}
    self.filename = filename
    self.zipfile = zipfile.ZipFile(filename)

  def readcsv(self, filemame):
    with self.zipfile.open(filemame) as f:
      data = csv.DictReader(f)
      for i in data:
        yield i
        
  def read(self, filename):
    if filename in self.cache:
      return self.cache[filename]
    try:
      data = list(self.readcsv(filename))
    except KeyError:
      data = []
    self.cache[filename] = data
    return data
    
  def stops_centroid(self):
    import ogr, osr
    multipoint = ogr.Geometry(ogr.wkbMultiPoint)
    # Todo: Geographic center, or simple average?
    # spatialReference = osr.SpatialReference()
    # spatialReference.SetWellKnownGeogCS("WGS84")
    # multipoint.AssignSpatialReference(spatialReference)    
    stops = self.read('stops.txt')
    for stop in stops:
      point = ogr.Geometry(ogr.wkbPoint)
      # point.AssignSpatialReference(spatialReference)
      point.AddPoint(float(stop['stop_lat']), float(stop['stop_lon']))
      multipoint.AddGeometry(point)
    point = multipoint.Centroid()
    return (point.GetX(), point.GetY())
    
  def stops_geohash(self, debug=False):
    stops = self.read('stops.txt')
    centroid = self.stops_centroid()
    centroid_geohash = geohash.encode(centroid)
    stops_geohash = [
      geohash.encode((float(stop['stop_lat']), float(stop['stop_lon'])))
      for stop in stops
    ]
    for i in range(1, len(centroid_geohash)):
      g = centroid_geohash[0:i]
      n = set(geohash.neighbors(g).values())
      n.add(g[0:i])
      unbounded = [s for s in stops_geohash if (s[0:i] not in n)]
      if debug:
        print "i:", i, "g:", g, "n:", n, "stops:", len(stops_geohash), "unbounded:", len(unbounded), "pct: %0.2f"%((len(unbounded)/float(len(stops_geohash)))*100.0)
        if unbounded:
          print "unbounded prefixes:", set(s[0:i] for s in unbounded)
          print "unbounded all:", unbounded
      if unbounded:        
        break
    return g[0:-1]
      

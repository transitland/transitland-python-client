"""GTFS tools."""
import zipfile
import csv

import geohash

class GTFSObject(object):
  def __init__(self, data):
    self.data = data    
  
  def __getitem__(self, key, default=None):
    return self.data.get(key, default)
  
  def __getitem__(self, key):
    if key in self.data:
      return self.data[key]
    elif key == 'geohash':
      return self.geohash()
    elif key == 'onestop':
      return self.onestop()
    elif key == 'coords':
      return self.coords()
    else:
      raise KeyError(key)
      
  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default
    
  def coords(self):
    raise NotImplementedError  
    
  def onestop(self):
    raise NotImplementedError

  def geohash(self):
    self.data['geohash'] = geohash.encode(self.coords())[:10]
    return self.data['geohash']

class GTFSAgency(GTFSObject):
  pass
  
class GTFSRoute(GTFSObject):
  pass
  
class GTFSStop(GTFSObject):
  def coords(self):
    self.data['coords'] = float(self.data['stop_lat']), float(self.data['stop_lon'])
    return self.data['coords']

class GTFSStation(GTFSObject):
  pass

class GTFSReader(object):
  factories = {
    'agency.txt': GTFSAgency,
    'routes.txt': GTFSRoute,
    'stops.txt': GTFSStop,
    None: GTFSObject
  }

  def __init__(self, filename):
    self.cache = {}
    self.filename = filename
    self.zipfile = zipfile.ZipFile(filename)

  def readcsv(self, filename):
    factory = self.factories.get(filename) or self.factories.get(None)
    with self.zipfile.open(filename) as f:
      data = csv.DictReader(f)
      for i in data:
        yield factory(i)
        
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
    # spatialReference = osr.SpatialReference() ...
    stops = self.read('stops.txt')
    for stop in stops:
      point = ogr.Geometry(ogr.wkbPoint)
      point.AddPoint(stop.coords()[0], stop.coords()[1])
      multipoint.AddGeometry(point)
    point = multipoint.Centroid()
    return (point.GetX(), point.GetY())
    
  def stops_geohash(self, debug=False):
    centroid = self.stops_centroid()
    points = [stop.coords() for stop in self.read('stops.txt')]
    return geohash.neighborsfit(centroid, points)

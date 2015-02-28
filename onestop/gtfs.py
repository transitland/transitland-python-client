"""GTFS tools."""
import zipfile
import unicodecsv
import csv
import re

import geohash

REPLACE = []
ABBR = [
  'street', 
  'st',
  'sts',
  'ctr',
  'center',
  'ave', 
  'avenue', 
  'av',
  'boulevard', 
  'blvd', 
  'road', 
  'rd', 
  'alley', 
  'aly', 
  'way', 
  'parkway', 
  'pkwy', 
  'lane',
  'ln',
  'hwy',
  'court',
  'ct',
]

for i in ABBR:
  REPLACE.append([r'\b%s\b'%i, ''])

REPLACE.extend([
  [r'\'',''],
  [r'\.',''],
  [r' - ',':'],
  [r'&',':'],
  [r'@',':'],
  [r'\/',':'],
  [r' ','']
])

def mangle(s):
  s = s.lower()
  for a,b in REPLACE:
    s = re.sub(a,b,s)
  return s

class GTFSObject(object):
  onestop_type = None
  
  def __init__(self, data, feed=None):
    self.data = data    
    self.feed = feed
    self.cache = {}
  
  def __getitem__(self, key, default=None):
    return self.data.get(key, default)
  
  def __getitem__(self, key):
    if key in self.data:
      return self.data[key]
    elif key == 'geohash':
      self.data['geohash'] = self.geohash()
      return self.data['geohash']
    elif key == 'onestop':
      self.data['onestop'] = self.onestop()
      return self.data['onestop']
    else:
      raise KeyError(key)
      
  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default
  
  def items(self):
    return [(k,self[k]) for k in self.keys()]
    
  def keys(self):
    return self.data.keys() + ['geohash', 'onestop']
  
  def name(self):
    raise NotImplementedError  

  def onestop(self):
    return '%s-%s-%s'%(self.onestop_type, self.geohash(), mangle(self.name()))

  def geohash(self):
    raise NotImplementedError  

  def point(self):
    raise NotImplementedError  
    
  def bbox(self):
    raise NotImplementedError    
    
  def geojson(self):
    raise NotImplementedError    

class GTFSAgency(GTFSObject):
  onestop_type = 'o'

  def name(self):
    return self['agency_name']

  def geohash(self, debug=False):
    # Filter stops without valid coordinates...
    points = [s.point() for s in self.stops() if s.point()]
    if not points:
      raise ValueError("Cannot create geohash with no stops.")
    centroid = self._stops_centroid()
    return geohash.neighborsfit(centroid, points)

  def point(self):
    bbox = self.bbox()
    return [
      (bbox[0]+bbox[2])/2,
      (bbox[1]+bbpx[3])/2      
    ]

  def bbox(self):
    points = [s.point() for s in self.stops()]
    if not points:
      raise ValueError("Cannot find bbox with no stops.")
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return [
      min(lons),
      min(lats),
      max(lons),
      max(lats)
    ]

  def geojson(self):
    return {
      'type': 'FeatureCollection',
      'features': [s.geojson() for s in self.stops()],
      'properties': dict((k,v) for k,v in self.items() if k != 'geometry'),
      'bbox': self.bbox()
    }

  def routes(self):
    if 'routes' in self.cache:
      return self.cache['routes']
    self.cache['routes'] = [route for route in self.feed.read('routes.txt') if route.get('agency_id') == self.get('agency_id')]
    return self.cache['routes']
    
  def trips(self):
    if 'trips' in self.cache:
      return self.cache['trips']
    route_ids = set(route.get('route_id') for route in self.routes())
    self.cache['trips'] = [trip for trip in self.feed.read('trips.txt') if trip.get('route_id') in route_ids]
    return self.cache['trips']
    
  def stop_times(self):
    if 'stop_times' in self.cache:
      return self.cache['stop_times']
    trip_ids = set(trip.get('trip_id') for trip in self.trips())
    self.cache['stop_times'] = [s for s in self.feed.readcsv('stop_times.txt') if s.get('trip_id') in trip_ids]
    return self.cache['stop_times']  
    
  def stops(self):
    if 'stops' in self.cache:
      return self.cache['stops']
    stop_ids = set(s.get('stop_id') for s in self.stop_times())
    self.cache['stops'] = [s for s in self.feed.read('stops.txt') if s.get('stop_id') in stop_ids]
    return self.cache['stops']
    
  def _stops_centroid(self):
    # Todo: Geographic center, or simple average?
    import ogr, osr
    multipoint = ogr.Geometry(ogr.wkbMultiPoint)
    # spatialReference = osr.SpatialReference() ...
    stops = [stop for stop in self.stops() if stop.point()]
    for stop in stops:
      point = ogr.Geometry(ogr.wkbPoint)
      point.AddPoint(stop.point()[1], stop.point()[0])
      multipoint.AddGeometry(point)
    point = multipoint.Centroid()
    return (point.GetY(), point.GetX())
    
class GTFSRoute(GTFSObject):
  onestop_type = 'r'

  def name(self):
    return self['route_name']
  
class GTFSStop(GTFSObject):
  onestop_type = 's'

  def name(self):
    return self['stop_name']

  def geohash(self):
    self.data['geohash'] = geohash.encode(self.point())[:10]
    return self.data['geohash']
    
  def point(self):
    if 'stop_lon' not in self.data or 'stop_lat' not in self.data:
      raise ValueError("Point is missing geometry.")
    self.data['point'] = float(self.data['stop_lon']), float(self.data['stop_lat'])
    return self.data['point']

  def bbox(self):
    c = self.point()
    return [c[0], c[1], c[0], c[1]]

  def geojson(self):
    return {
      'type': 'Feature',
      'geometry': {
        "type": 'Point',
        "coordinates": self.point(),
      },
      'properties': dict((k,v) for k,v in self.items() if k != 'geometry'),
      'bbox': self.bbox()
    }

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
      data = unicodecsv.DictReader(f, encoding='utf-8-sig')
      for i in data:
        yield factory(i, feed=self)
    return
        
  def read(self, filename):
    if filename in self.cache:
      return self.cache[filename]
    try:
      data = list(self.readcsv(filename))
    except KeyError:
      data = []
    self.cache[filename] = data
    return data
    
  def agencies(self):
    return self.read('agency.txt')  
    

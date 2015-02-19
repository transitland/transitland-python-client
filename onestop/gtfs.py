"""GTFS tools."""
import zipfile
import csv

import geohash

class GTFSReader(object):
  def __init__(self, filename):
    self.zipfile = zipfile.ZipFile(filename)

  def readcsv(self, filemame):
    with self.zipfile.open(filemame) as f:
      data = csv.DictReader(f)
      for i in data:
        yield i
    
  def stops_centroid(self):
    import ogr, osr
    multipoint = ogr.Geometry(ogr.wkbMultiPoint)
    # Todo: Geographic center, or simple average?
    # spatialReference = osr.SpatialReference()
    # spatialReference.SetWellKnownGeogCS("WGS84")
    # multipoint.AssignSpatialReference(spatialReference)    
    for stop in self.readcsv('stops.txt'):
      point = ogr.Geometry(ogr.wkbPoint)
      # point.AssignSpatialReference(spatialReference)
      point.AddPoint(float(stop['stop_lon']), float(stop['stop_lat']))
      multipoint.AddGeometry(point)
    point = multipoint.Centroid()
    return (point.GetX(), point.GetY())
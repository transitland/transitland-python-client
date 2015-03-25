"""Geometry utilities."""
import mzgeohash

def geohash_features(features):
  # Filter stops without valid coordinates...
  points = [feature.point() for feature in features if feature.point()]
  if not points:
    raise errors.OnestopNoPoints("Not enough points.")
  c = centroid_points(points)
  return mzgeohash.neighborsfit(c, points)
  
def centroid_points(points):
  """Return the lon,lat centroid for features."""
  # Todo: Geographic center, or simple average?
  import ogr, osr
  multipoint = ogr.Geometry(ogr.wkbMultiPoint)
  # spatialReference = osr.SpatialReference() ...
  for point in points:
    p = ogr.Geometry(ogr.wkbPoint)
    p.AddPoint(point[1], point[0])
    multipoint.AddGeometry(p)
  point = multipoint.Centroid()
  return (point.GetY(), point.GetX())
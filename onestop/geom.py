"""Geometry utilities."""
import mzgeohash

import errors

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
  x = sum(i[0] for i in points)
  y = sum(i[1] for i in points)
  return x/len(points), y/len(points)

"""Geometry utilities."""
import mzgeohash

import errors

def geohash_features(features):
  """mzgeohash.neighborsfit on a list of features that implement point()."""
  # Filter stops without valid coordinates...
  points = [feature.point() for feature in features if feature.point()]
  if not points:
    raise errors.NoPointsError("Not enough points.")
  c = centroid(points)
  return mzgeohash.neighborsfit(c, points)
  
def centroid(points):
  """Return the lon,lat simple geometric centroid for features."""
  # Todo: Geographic center, or simple average?
  x = sum(i[0] for i in points)
  y = sum(i[1] for i in points)
  return x/len(points), y/len(points)

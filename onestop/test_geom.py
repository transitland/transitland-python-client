"""Geometry unit tests."""
import unittest
import os

import errors
import geom

# Mock Data
EXPECT = [
  [-122.297461, 37.537814],
  [-122.19779, 37.464645],
  [-121.610049, 37.085225],
  [-122.197869, 37.464584],
  [-122.392404, 37.757583],
  [-121.997135, 37.370484],
  [-122.3449, 37.580197],
  [-121.901985, 37.330196],
  [-122.275816, 37.520844],
  [-122.386832, 37.599797],
  [-122.26015, 37.50805],
  [-121.566225, 37.003485],
  [-122.164697, 37.443405],
  [-121.842037, 37.284062],
  [-122.405018, 37.655946],
  [-121.841955, 37.284102],
  [-121.650304, 37.129321],
  [-121.797643, 37.252422],
  [-121.566088, 37.003538],
  [-122.412076, 37.631108],
  [-122.260266, 37.507933],
  [-122.36265, 37.58764],
  [-122.39188, 37.757599],
  [-122.401586, 37.709537],
  [-122.231936, 37.486159],
  [-122.309338, 37.552938],
  [-122.107125, 37.407277],
  [-122.141978, 37.429333],
  [-122.40198, 37.709544],
  [-122.182297, 37.454856],
  [-122.031423, 37.378789],
  [-122.141927, 37.429365],
  [-122.386647, 37.59988],
  [-121.610936, 37.086653],
  [-121.650244, 37.129363],
  [-122.182405, 37.454745],
  [-121.914677, 37.342338],
  [-122.164614, 37.443475],
  [-122.362708, 37.587552],
  [-122.031372, 37.378916],
  [-122.394992, 37.77639],
  [-121.9146, 37.342384],
  [-122.394935, 37.776348],
  [-122.411968, 37.631128],
  [-122.324092, 37.568294],
  [-122.345075, 37.580186],
  [-122.323851, 37.568087],
  [-122.232, 37.486101],
  [-122.107069, 37.407323],
  [-121.883999, 37.31175],
  [-121.797683, 37.252379],
  [-121.936135, 37.353189],
  [-121.883721, 37.31174],
  [-122.075956, 37.394459],
  [-122.075994, 37.394402],
  [-122.297349, 37.537868],
  [-121.903011, 37.329239],
  [-122.40487, 37.65589],
  [-121.93608, 37.353238],
  [-121.903173, 37.329231],
  [-122.309608, 37.552994],
  [-121.997114, 37.370598],
  [-122.275738, 37.52089],
  [-121.883403, 37.311638]
]

class Point(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    
  def point(self):
    return self.x, self.y

class Test_geohash_features(unittest.TestCase):
  def test_geohash_features(self):
    data = [Point(x,y) for x,y in EXPECT]
    assert geom.geohash_features(data) == '9q9'
    
  def test_geohash_features_no_points(self):
    with self.assertRaises(errors.OnestopNoPoints):
      geom.geohash_features([])
    
class Test_centroid_points(unittest.TestCase):
  def test_centroid_points(self):
    expect = (-122.11545060937499, 37.44463196875001)
    data = geom.centroid(EXPECT)
    for i,j in zip(data, expect):
      self.assertAlmostEqual(i,j)
    
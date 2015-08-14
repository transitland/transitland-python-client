"""Transitland Datastore interface."""
import json
import urllib
import urllib2
import time

import entities
import errors

class Datastore(object):
  def __init__(self, endpoint, apitoken=None, debug=False, log=None):
    self.host = endpoint
    self.debug = debug
    self.apitoken = apitoken
    self.log = log or (lambda x:x)

  def _request(self, endpoint, data=None):
    req = urllib2.Request('%s/%s'%(self.host, endpoint))
    req.add_header('Content-Type', 'application/json')
    if self.apitoken:
      req.add_header('Authorization', 'Token token=%s'%self.apitoken)
    try:
      if data is not None:
        response = urllib2.urlopen(req, json.dumps(data))
      else:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e: 
      raise errors.DatastoreError(e.reason, response_code=e.code, response_body=e.read())
    except urllib2.URLError, e:
      raise errors.DatastoreError(e.reason)
    except Exception, e:
      raise
    data = response.read()
    try:
      return json.loads(data)
    except ValueError, e:
      raise errors.DatastoreError("Invalid JSON response", response_code=response.code, response_body=data)

  def postjson(self, endpoint, data=None):
    return self._request(endpoint, data=data or {})

  def getjson(self, endpoint):
    return self._request(endpoint)

  def stops(self, point=None, radius=1000, identifier=None):
    endpoint = '/api/v1/stops'
    if identifier:
      endpoint = '/api/v1/stops?identifier=%s'%(identifier)
    if point:
      endpoint = '/api/v1/stops?lon=%0.8f&lat=%0.8f&r=%d'%(
        point[0],
        point[1],
        radius
      )
    response = self.getjson(endpoint)
    stops = set()
    for i in response['stops']:
      e = entities.Stop.from_json(i)
      stops.add(e)
    return stops


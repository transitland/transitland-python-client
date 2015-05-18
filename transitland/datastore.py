"""Transitland Datastore interface."""
import json
import urllib
import urllib2

import entities

class Datastore(object):
  def __init__(self, endpoint, apitoken=None, debug=False):
    self.endpoint = endpoint
    self.debug = debug
    self.apitoken = apitoken

  def postjson(self, endpoint, data):
    if self.debug:  # pragma: no cover
      print "====== POST: %s ======"%endpoint
      print data
    req = urllib2.Request(endpoint)
    req.add_header('Content-Type', 'application/json')
    if self.apitoken:
      req.add_header('Authorization', 'Token token=%s'%self.apitoken)
    response = urllib2.urlopen(req, json.dumps(data))
    ret = json.loads(response.read())
    if self.debug:  # pragma: no cover
      print "--> Response: "
      print ret
    return ret

  def getjson(self, endpoint):
    if self.debug:  # pragma: no cover
      print "====== GET: %s ======"%endpoint
    req = urllib2.Request(endpoint)
    if self.apitoken:
      req.add_header('Authorization', 'Token token=%s'%self.apitoken)
    response = urllib2.urlopen(req)
    ret = json.loads(response.read())
    if self.debug: # pragma: no cover
      print "--> Response: "
      print ret
    return ret

  def changeset(self, data, rels=True):
    onestop_types = {
      's': 'stop',
      'r': 'route',
      'o': 'operator'
    }  
    return {
       "changeset": {
         "whenToApply": "instantlyIfClean",
         "payload": {
           "changes": [
             {
               "action": "createUpdate",
               onestop_types[data['onestopId'][0]]: data
             }
           ]
         }
       }
    }
    
  def update_entity(self, entity, rels=True):
    data = self.changeset(entity.json_datastore(rels=rels))
    endpoint = '%s/api/v1/changesets/'%(self.endpoint)
    self.postjson(endpoint, data)

  def stops(self, point=None, radius=1000, identifier=None):
    endpoint = '%s/api/v1/stops'%(self.endpoint)
    if identifier:
      endpoint = '%s/api/v1/stops?identifier=%s'%(
        self.endpoint,
        identifier
      )
    if point:
      endpoint = '%s/api/v1/stops?lon=%0.8f&lat=%0.8f&r=%d'%(
        self.endpoint, 
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

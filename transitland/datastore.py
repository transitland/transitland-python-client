"""Transitland Datastore interface."""
import json
import urllib
import urllib2

import mzgtfs.feed
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

  def update_operator(self, operator):
    # Entities to post.
    entities = operator.stops() # | operator.routes()
    # Note: Agencies must be created before routes/stops.
    # Post without relationships
    self.update_entity(operator, rels=False)
    for entity in entities:
      self.update_entity(entity, rels=False)
    # Update relationships
    self.update_entity(operator)
    for entity in entities:
      self.update_entity(entity)

  def search_entity(self, entity, radius=1000):
    point = entity.point()
    endpoint = '%s/api/v1/stops?lon=%0.8f&lat=%0.8f&r=%d'%(
      self.endpoint, 
      point[0], 
      point[1],
      radius
    )
    response = self.getjson(endpoint)
    search_entities = set()
    for i in response['stops']:
      e = entities.Stop(
        name=i['name'],
        geometry=i['geometry'],
        onestop_id=i['onestopId']
      )
      search_entities.add(e)
    return search_entities

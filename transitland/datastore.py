"""Transitland Datastore interface."""
import json
import urllib
import urllib2

import entities

class Datastore(object):
  ONESTOP_TYPES = {
    's': 'stop',
    'r': 'route',
    'o': 'operator'
  }  
  
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

  def update_entity(self, entity, rels=True):
    return self.update_entities([entity])
    
  def _entity_without_rels(self, entity):
    skip = ['features', 'serves', 'doesNotServe', 'servedBy', 'notServedBy']
    data = entity.json()
    for key in skip:
      data.pop(key, None)
    return data
    
  def _entity_rels(self, entity):
    skip = ['features']
    data = entity.json()
    for key in skip:
      data.pop(key, None)
    return data

  def update_entities(self, entities):
    # Sort.
    ents = []
    for prefix in ('o', 'r', 's'):
      ents += filter(lambda x:x.onestop_type==prefix, entities)
    for entity in ents:
      print entity.onestop()
    # 
    changes = []
    # Without rels
    for entity in ents:
      change = {}
      change['action'] = 'createUpdate'
      change[self.ONESTOP_TYPES[entity.onestop_type]] = self._entity_without_rels(entity)
      changes.append(change)
    # With rels
    for entity in ents:
      change = {}
      change['action'] = 'createUpdate'
      change[self.ONESTOP_TYPES[entity.onestop_type]] = self._entity_rels(entity)
      changes.append(change)
    changeset = {
      'changeset': {
        'whenToApply': 'instantlyIfClean',
        'payload': {
          'changes': changes
        }
      }
    }
    endpoint = '%s/api/v1/changesets/'%(self.endpoint)
    self.postjson(endpoint, changeset)

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

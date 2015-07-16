"""Transitland Datastore interface."""
import json
import urllib
import urllib2
import time

import entities
import errors

class Datastore(object):
  ONESTOP_TYPES = {
    's': 'stop',
    'r': 'route',
    'o': 'operator'
  }

  def __init__(self, endpoint, apitoken=None, debug=False):
    self.host = endpoint
    self.debug = debug
    self.apitoken = apitoken

  def _request(self, endpoint, data=None):
    data = data or {}
    req = urllib2.Request('%s/%s'%(self.host, endpoint))
    req.add_header('Content-Type', 'application/json')
    if self.apitoken:
      req.add_header('Authorization', 'Token token=%s'%self.apitoken)
    try:
      if data:
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
    return self._request(endpoint, data=data)

  def getjson(self, endpoint):
    return self._request(endpoint)

  def update_entity(self, entity, rels=True):
    return self.update_entities([entity])

  def _change(self, entity, keys, action='createUpdate'):
    data = entity.json()
    change = {}
    for key in keys:
      if key in data:
        change[key] = data.get(key)
    if 'identifiers' in keys:
        change['identifiedBy'] = change.pop('identifiers')
    return {
      'action': action,
      self.ONESTOP_TYPES[entity.onestop_type]: change
    }

  def update_entities(self, entities, whenToApply='instantlyIfClean'):
    # Sort
    ents = []
    for prefix in ('o', 'r', 's'):
      ents += filter(lambda x:x.onestop_type==prefix, entities)
    # Changes
    keys = [
      'onestopId',
      'name',
      'geometry',
      'tags',
      'identifiers',
      'operatedBy',
      'servedBy'
    ]
    # Post
    changeset = self.postjson(
      '/api/v1/changesets',
      {"changeset": {"payload": {}}} # empty changeset
    )
    for count, entity in enumerate(ents):
      t = time.time()
      data = {
        'changes': [self._change(entity, keys)]
      }
      self.postjson(
        '/api/v1/changesets/%s/append'%changeset['id'],
        data
      )
      # print 'Entity %s of %s: %s bytes, %0.2f seconds'%(count, len(ents), len(json.dumps(data)), time.time() - t)
    self.postjson('/api/v1/changesets/%s/apply'%changeset['id'])

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

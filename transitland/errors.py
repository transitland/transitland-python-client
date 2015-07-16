##### Exceptions #####

class ExistingIdentifierError(KeyError):
  pass

class NoPointsError(ValueError):
  pass
  
class InvalidFeedRegistryError(ValueError):
  pass
  
class InvalidChecksumError(ValueError):
  pass
  
class DatastoreError(Exception):
  def __init__(self, message, response_code=None, response_body=None):
    super(DatastoreError, self).__init__(message)
    self.response_code = response_code
    self.response_body = response_body

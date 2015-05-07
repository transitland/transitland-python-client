##### Exceptions #####

class ExistingIdentifierError(KeyError):
  pass

class NoPointsError(ValueError):
  pass
  
class InvalidFeedRegistryError(ValueError):
  pass
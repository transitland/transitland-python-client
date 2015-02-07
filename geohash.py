"""A simple GeoHash implementation."""

BASESEQUENCE = [
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    'b',
    'c',
    'd',
    'e',
    'f',
    'g',
    'h',
    'j',
    'k',
    'm',
    'n',
    'p',
    'q',
    'r',
    's',
    't',
    'u',
    'v',
    'w',
    'x',
    'y',
    'z']

# Forward and reverse base 32 map
BASE32MAP = dict((k,count) for count,k in enumerate(BASESEQUENCE))
BASE32MAPR = dict((count,k) for count,k in enumerate(BASESEQUENCE))

def geobits_to_float(bits, lower=-90.0, middle=0.0, upper=90.0):
  """Convert GeoHash bits to a float."""
  for i in bits:
    if i:
      lower = middle
    else:
      upper = middle
    middle = (upper + lower) / 2
  return middle
  
def float_to_geobits(value, lower=-90.0, middle=0.0, upper=90.0, length=15):
  """Convert a float to a list of GeoHash bits."""
  ret = []
  for i in range(length):
    if value >= middle:
      lower = middle
      ret.append(1)
    else:
      upper = middle
      ret.append(0)
    middle = (upper + lower) / 2
  return ret

def geohash_to_geobits(value):
  """Convert a GeoHash to a list of GeoHash bits."""
  b = map(BASE32MAP.get, value)
  ret = []
  for i in b:
    out = []
    for z in range(5):
      out.append(i & 0b1)
      i = i >> 1
    ret += out[::-1]
  return ret
  
def geobits_to_geohash(value):
  """Convert a list of GeoHash bits to a GeoHash."""
  ret = []
  # Get 5 bits at a time
  for i in (value[i:i+5] for i in xrange(0, len(value), 5)):
    # Convert binary to integer
    # Note: reverse here, the slice above doesn't work quite right in reverse.
    total = sum([(bit*2**count) for count,bit in enumerate(i[::-1])])
    ret.append(BASE32MAPR[total])
  # Join the string and return
  return "".join(ret)
      
def decode(value):
  """Decode a geohash. Returns a (lat,lon) pair."""
  # Get the GeoHash bits
  bits = geohash_to_geobits(value)
  # Unzip the GeoHash bits.
  lon = bits[0::2]
  lat = bits[1::2]
  # Convert to lat/lon
  return (
    geobits_to_float(lat), 
    geobits_to_float(lon, lower=-180.0, upper=180.0)
  )

def encode(latlon, length=12):
  """Encode a (lat,lon) pair to a GeoHash."""
  # Half the length for each component.
  length /= 2
  lat = float_to_geobits(latlon[0], length=length*5)
  lon = float_to_geobits(latlon[1], lower=-180.0, upper=180.0, length=length*5)
  # Zip the GeoHash bits.
  ret = []
  for a,b in zip(lat,lon):
    ret.append(b)
    ret.append(a)
  return geobits_to_geohash(ret)
  
if __name__ == "__main__":
  # A little command line utility goes here.
  pass
  
"""Helpful utilitors."""
import json

def json_dump_pretty(data, f):
  json.dump(
    data,
    f,
    sort_keys=True,
    indent=4,
    separators=(',', ': ')
  )

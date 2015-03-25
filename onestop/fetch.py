"""Fetch Onestop """
import onestop
import argparse

import registry

def run():
  parser = argparse.ArgumentParser(description='Read Onestop Registry')
  parser.add_argument('--onestop', help='Onestop Registry path', default='.')
  parser.add_argument('feedids', nargs='*', help='Onestop Feed IDs')
  args = parser.parse_args()

  # Onestop Registry
  r = registry.OnestopRegistry(path=args.onestop)
  feedids = args.feedids or r.feeds()
  for feedid in feedids:
    feed = r.feed(feedid)
    filename = '%s.zip'%feedid
    feed.fetch(filename)
    
if __name__ == "__main__":
  run()
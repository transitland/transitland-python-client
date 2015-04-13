"""Fetch Onestop feeds."""
import onestop
import argparse

import registry

def run():
  parser = argparse.ArgumentParser(description='Read Onestop Registry')
  parser.add_argument('feedids', nargs='*', help='Onestop Feed IDs')
  parser.add_argument('--onestop', help='Onestop Registry path', default='.')
  parser.add_argument('--all', help='Update all feeds', action='store_true')
  parser.add_argument('--verbose', help='Verbosity', type=int, default=1)
  args = parser.parse_args()

  # Onestop Registry
  r = registry.OnestopRegistry(path=args.onestop)
  feedids = args.feedids
  if args.all:
    feedids = r.feeds()
  if len(feedids) == 0:
    raise Exception("No feeds specified! Try --all")
  for feedid in feedids:
    feed = r.feed(feedid)
    filename = '%s.zip'%feedid
    feed.download(filename, debug=args.verbose)
    
if __name__ == "__main__":
  run()
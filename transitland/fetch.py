"""Fetch Transitland Feed Registry feeds."""
import argparse

import registry
import util

def run():
  parser = argparse.ArgumentParser(description='Fetch Transitland Feeds')
  parser.add_argument('feedids', nargs='*', help='Feed IDs')
  parser.add_argument('--registry', help='Feed Registry Path')
  parser.add_argument('--all', help='Update all feeds', action='store_true')
  parser.add_argument('--verbose', help='Verbosity', type=int, default=1)
  args = parser.parse_args()

  # Transitland Feed Registry
  r = registry.FeedRegistry(path=args.registry)
  feedids = args.feedids
  if args.all:
    feedids = r.feeds()
  if len(feedids) == 0:
    raise Exception("No feeds specified! Try --all")
  for feedid in feedids:
    feed = r.feed(feedid)
    filename = '%s.zip'%feed.onestop()
    print "Downloading: %s -> %s"%(feed.url(), filename)
    feed.download(filename)

if __name__ == "__main__":
  run()
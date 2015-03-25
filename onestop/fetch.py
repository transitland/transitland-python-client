"""Fetch Onestop """
import onestop
import argparse

def run():
  parser = argparse.ArgumentParser(description='Read Onestop Registry')
  parser.add_argument('path', help='Path to Onestop Registry')
  parser.add_argument('feeds', nargs='*', help='Fetch Onestop Feeds')
  parser.add_argument('--prefix', help='Fetch Onestop Feeds with GeoHash Prefix.')
  args = parser.parse_args()
  # Onestop Registry
  registry = onestop.OnestopRegistry(path=args.path)    
  # Use generator
  if args.feeds:
    feeds = (registry.load_feed(i) for i in args.feeds)
  else:
    feeds = registry.load_feeds()
  # Fetch each feed
  for feed in feeds:
    print "Fetching feed %s: %s"%(feed.onestopId, feed.url)
    feed.fetch('%s.zip'%feed.onestopId)
    
if __name__ == "__main__":
  run()
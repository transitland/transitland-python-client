# Onestop-ID Registry Python Client

[![Circle CI](https://circleci.com/gh/transitland/onestop-id-python-client.png?style=badge)](https://circleci.com/gh/transitland/onestop-id-python-client)

This is a Python client for the [Onestop ID Registry](https://github.com/transitland/onestop-id-registry).

## Installation

Installation using pip:

```
pip install onestop
```

Alternatively, [download from PyPi](https://pypi.python.org/pypi/onestop) or clone this repository, and install using setup.py:

```
python ./setup.py install
```

The dependencies [mzgeohash](https://github.com/transitland/mapzen-geohash) and [mzgtfs](https://github.com/transitland/mapzen-gtfs) will be automatically installed using the above methods.


## Opening the Onestop ID Registry

First, make sure you have a copy of the current Onestop ID Registry. This can be accomplished through a git clone:

```
git clone https://github.com/transitland/onestop-id-registry.git
```

Then, create a registry reader with onestop.registry.OnestopRegistry, passing the path to the registry as the argument.

```
>>> import onestop.registry
>>> registry = onestop.registry.OnestopRegistry('.')
```

You can now list the known feeds and operators:

```
>>> registry.feeds()
['f-9q5-lacmta', 'f-9q8-samtrans', 'f-9q8y-sanfranciscomunicipaltransportationagency', 'f-9q9-actransit', 'f-9q9-caltrain', 'f-9q9-vta', 'f-9vk-mtaharriscounty', 'f-c20-trimet', 'f-c23-kingcounty', 'f-c28-translink', 'f-dhw-miamidade', 'f-dnh-marta', 'f-dp3-cta', 'f-dpz8-ttc', 'f-dq-mtamaryland', 'f-dqc-wmata', 'f-dr5r-nyctsubway', 'f-dr5r-panynjpath', 'f-drt-mbta']
>>> registry.operators()
['o-9q5-metrolosangeles', 'o-9q8-samtrans', 'o-9q8y-sanfranciscomunicipaltransportationagency', 'o-9q9-actransit', 'o-9q9-bayarearapidtransit', 'o-9q9-caltrain', 'o-9q9-vta', 'o-9vk-metropolitantransitauthorityofharriscounty', 'o-c20-trimet', 'o-c22y-kingcountymarinedivison', 'o-c23-metrotransit', 'o-c23n-soundtransit', 'o-c23nb-cityofseattle', 'o-c28-translink', 'o-c2b-westcoastexpress', 'o-c2b8-britishcolumbiarapidtransitcompany', 'o-dhw-miamidadetransit', 'o-dnh-metropolitanatlantarapidtransitauthority', 'o-dp3-chicagotransitauthority', 'o-dpz8-ttc', 'o-dq-mtaofficeoflocaltransitsupport', 'o-dqc-marylandtransitadministration', 'o-dqc-met', 'o-dqcjr-dccirculator', 'o-dr5r-mtanewyorkcitytransit', 'o-dr5r-portauthoritytranshudsoncorporation', 'o-drt-mbta', 'o-drt3p-massport']
```

## Working with a feed

A specific feed can be read with OnestopRegistry.feed(). The resulting OnestopFeed can be used to inspect the feed attributes, download the current version of the feed, etc.

```
>>> feed = registry.feed('f-9q9-caltrain')
>>> feed.operatorsInFeed()
'o-9q9-caltrain'
>>> feed.url()
'http://www.caltrain.com/Assets/GTFS/caltrain/GTFS-Caltrain-Devs.zip'
>>> feed.download('caltrain-current-gtfs.zip')
```

## Operators, routes, and stops

Each feed contains data for one or more operators, which can be read using OnestopRegistry.operator(). The resulting OnestopOperator then provides the associated routes, stops, and references to other databases.

```
>>> operator = registry.operator('o-9q9-caltrain')
>>> len(operator.stops())
64
>>> [(stop.onestop(), stop.point()) for stop in operator.stops()][:5]
[('s-9q9k658fd1-sanjosediridoncaltrain', [-121.903173, 37.329231]), ('s-9q9j8u2f59-haywardparkcaltrain', [-122.309608, 37.552994]), ('s-9q9hxgh7t0-lawrencecaltrain', [-121.997114, 37.370598]), ('s-9q9j3w3x0b-belmontcaltrain', [-122.275738, 37.52089]), ('s-9q9k62rhnc-tamiencaltrainstation', [-121.883403, 37.311638])]
>>> [(route.onestop(), route.name()) for route in operator.routes()]
[('r-9q9-local', 'Local'), ('r-9q9k6-tamien~sanjosediridoncaltrainshuttle', 'Tamien / San Jose Diridon Caltrain Shuttle'), ('r-9q9-bullet', 'Bullet'), ('r-9q9-limited', 'Limited')]
```

## Download current GTFS feeds

The current versions of GTFS feeds can be downloaded to the current directory using onestop.fetch:

```
$ python -m onestop.fetch f-9q9-caltrain
Downloading: http://www.caltrain.com/Assets/GTFS/caltrain/GTFS-Caltrain-Devs.zip -> f-9q9-caltrain.zip
```

The "--all" option can also be used to download all feeds in the registry. Only updated feeds will be downloaded:

```
$ python -m onestop.fetch --all
Downloading: http://developer.metro.net/gtfs/google_transit.zip -> f-9q5-lacmta.zip
Downloading: http://www.samtrans.com/Assets/GTFS/samtrans/SamTrans-GTFS.zip -> f-9q8-samtrans.zip
Downloading: http://archives.sfmta.com/transitdata/google_transit.zip -> f-9q8y-sanfranciscomunicipaltransportationagency.zip
...
```

## Bootstrapping a feed from a GTFS source

A Onestop Feed can be created from a GTFS url with onestop.bootstrap. Specify the URL with "--url" and the feed name with "--feedname":

```
$ python -m onestop.bootstrap --url http://developer.trimet.org/schedule/gtfs.zip --feedname trimet
Attempting to bootstrap feed from GTFS file...
Downloading: http://developer.trimet.org/schedule/gtfs.zip -> ./data/trimet-bootstrap.zip
Loading feed: trimet-bootstrap
Feed: f-c20-trimet
  Operators: 1
  Routes: 89
  Stops: 6879
Operator: TriMet
  Routes: 89
  Stops: 6879
```

A basic feed description will be written to the feeds directory that can then be annotated with details about licenses, additional identifiers, etc.

```json
{
    "feedFormat": "gtfs",
    "name": "trimet",
    "onestopId": "f-c20-trimet",
    "operatorsInFeed": [
        {
            "gtfsAgencyId": "trimet",
            "onestopId": "o-c20-trimet"
        }
    ],
    "sha1": "20ee818194ba0f3818a5823b705818597b7592e2",
    "tags": {},
    "url": "http://developer.trimet.org/schedule/gtfs.zip"
}
```

## Contributing

Please [open a Github issue](https://github.com/transitland/onestop-id-python-client/issues/new) with as much of the following information as yo're able to specify, or [contact us](#contact) for assistance.

## License

Unless otherwise indicated, the code used to build and maintain this registry is Copyright (C) 2014-2015 Mapzen and released under the [MIT license](http://opensource.org/licenses/MIT).

## Contact

Transitland is sponsored by [Mapzen](http://mapzen.com). Contact us with your questions, comments, or suggests: [hello@mapzen.com](mailto:hello@mapzen.com).

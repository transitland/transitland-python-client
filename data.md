# GTFS to Transitland

Many GTFS attributes are passed through to the Transitland data model, either as
attributes or as tags. A * indicates a required GTFS attribute.

## agency.txt

  * agency_id -> Operator.identifiers
  * agency_name* -> Operator.name
  * agency_timezone*
  * agency_url*
  * agency_phone
  * agency_lang
  * agency_fare_url

## stops.txt

  * stop_id* -> Stop.identifiers
  * stop_name* -> Stop.name
  * stop_lon*, stop_lat* -> Stop.geometry
  * location_type, parent_station -> as Stop/StopStation/StopEgress
  * stop_timezone
  * wheelchair_boarding
  * stop_desc
  * stop_url
  * zone_id

## routes.txt

  * route_id* -> Route.identifiers
  * route_short_name* -> Route.name
  * agency_id -> Route.operatedBy
  * shape_id from trips -> Route.geometry
  * route_type* (as vehicle_type)
  * route_long_name
  * route_desc
  * route_url
  * route_color, route_text_color

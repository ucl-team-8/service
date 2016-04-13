import moment from "moment";
import _ from "lodash";
import get from "./d3-request-promise";

/*

Contains data coercing functions for various entities on the API, since JSON
serializes certain datatypes.

Also contains functions that automatically request data, coerce types, and
return the processed data.

*/

export function parseDate(string) {
  return moment(string, "YYYY-MM-DDTHH:mm:ss").toDate();
}

export function serializeDate(date) {
  return moment(date).format("YYYY-MM-DDTHH:mm:ss");
}

// -----------------------------------------------------------------------------

export function trustDatatypes(d) {
  d.event_time = parseDate(d.event_time);
  d.origin_departure = parseDate(d.origin_departure);
  d.tiploc = d.tiploc.trim();
  return d;
}

export function getTrust() {
  return get("json", "/events/trust.json").then((data) => {
    data = data.result;
    data.forEach(trustDatatypes);
    return data;
  });
}

export function parseTrust(reports) {
  reports.forEach(trustDatatypes);
  return reports;
}

// -----------------------------------------------------------------------------

export function gpsDatatypes(d) {
  d.event_time = parseDate(d.event_time);
  return d;
}

export function getGPS() {
  return get("json", "/events/gps.json").then((data) => {
    data = data.result;
    data.forEach(gpsDatatypes);
    return data;
  });
}

export function parseGPS(reports) {
  reports.forEach(gpsDatatypes);
  return reports;
}

// -----------------------------------------------------------------------------

export function locationsDatatypes(d) {
  d.cif_pass_count = Number(d.cif_pass_count);
  d.cif_stop_count = Number(d.cif_stop_count);
  d.is_cif_stop = Boolean(d.is_cif_stop);
  d.latitude = Number(d.latitude);
  d.longitude = Number(d.longitude);
  d.easting = Number(d.easting);
  d.northing = Number(d.northing);
  return d;
}

export function getLocations() {
  return get("csv", "/static/data/locations_northern_rail_extract.csv").then(parseLocations);
}

export function parseLocations(locations) {
  locations.forEach(locationsDatatypes);
  return locations;
}

// -----------------------------------------------------------------------------

// old segments
export function getSegment(segment) {
  segment.matching.forEach(stop => {
    if (stop.trust) trustDatatypes(stop.trust);
    if (stop.gps) gpsDatatypes(stop.gps);
  });
  return segment;
}

export function getSegments() {
  return get("json", "/data/segments.json").then((data) => {
    data = data.results;
    data.forEach(segment => getSegment(segment));
    return data;
  });
}

// new segments
export function parseSegment(segment) {
  if (segment.origin_departure) segment.origin_departure = parseDate(segment.origin_departure);
  if (segment.start) segment.start = parseDate(segment.start);
  if (segment.end) segment.end = parseDate(segment.end);
  segment.trust.forEach(trustDatatypes);
  segment.gps.forEach(gpsDatatypes);
  segment.trust = _.sortBy(segment.trust, "event_time");
  segment.gps = _.sortBy(segment.gps, "event_time");
  return segment;
}

export function parseMatching(matching) {
  if (matching.origin_departure) matching.origin_departure = parseDate(matching.origin_departure);
  return matching;
}

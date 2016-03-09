import get from "./d3-async-get";

export function trustDatatypes(d) {
  d.event_time = new Date(d.event_time);
  d.origin_depart_time = new Date(d.origin_departure);
  d.tiploc = d.tiploc.trim();
}

export function getTrust() {
  return get("json", "/events/trust.json").then((data) => {
    data = data.result;
    data.forEach(trustDatatypes);
    return data;
  });
}

// -----------------------------------------------------------------------------

export function gpsDatatypes(d) {
  d.event_time = new Date(d.event_time);
}

export function getGPS() {
  return get("json", "/events/gps.json").then((data) => {
    data = data.result;
    data.forEach(gpsDatatypes);
    return data;
  });
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
}

export function getLocations() {
  return get("csv", "/static/data/locations_east_coast_extract.csv").then((data) => {
    data.forEach(locationsDatatypes);
    return data;
  });
}

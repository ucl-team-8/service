import _ from "lodash";
import d3 from "d3";
import L from "leaflet";

import RouteMap from "./route-map";
import { getSegments, getLocations } from "./data";

let transportLayer = new L.TileLayer("http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png")
    .setOpacity(0.15);

let map = new L.Map("map", {center: [53.5, -1.5], zoom: 7})
    .addLayer(transportLayer);

let routeMap = new RouteMap(map);

window.locations = {};

Promise.all([
  getSegments(),
  getLocations()
]).then(([segments, locations]) => {

  window.locations = _.keyBy(locations, "tiploc");

  let services = d3.nest()
    .key(d => d.headcode)
    .entries(segments);

  let serviceSegments = services[8].values;

  let serviceStops = getServiceStopsFromSegments(serviceSegments);
  let units = serviceSegments.map(getUnitStopsFromSegment);

  routeMap.plotServices([serviceStops]);
  routeMap.plotUnits(units);

});

function getServiceStopsFromSegments(segments) {
  return _(segments)
    .map(d => d.matching)
    .flatten()
    .map(d => d.trust)
    .uniqWith(_.isEqual)
    .compact()
    .sortBy(d => d.event_time)
    .value();
}

function getUnitStopsFromSegment(segment) {
  return _(segment.matching)
    .map(d => d.gps)
    .compact()
    .sortBy(d => d.event_time)
    .value();
}

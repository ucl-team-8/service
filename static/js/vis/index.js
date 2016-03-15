import _ from "lodash";
import d3 from "d3";
import L from "leaflet";

import RouteMap from "./map/route-map";
import { getSegments, getLocations } from "./utils/data";
import updateReports from "./reports/update-reports";
import noOverlap from "./utils/no-overlap-time-scale";

/*

IMPORTANT: All the code in this file is sort of hacked together and you probably
shouldn't add functionality here, instead make a new module or something.

*/

let transportLayer = new L.TileLayer("http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png")
    .setOpacity(0.15);

let map = new L.Map("map", {center: [53.5, -1.5], zoom: 7})
    .addLayer(transportLayer);

let reportsContainer = d3.select(".reports-svg")
    .attr("width", 300)
    .attr("height", 1500);

let routeMap = new RouteMap({ map });

window.locations = {};

Promise.all([
  getSegments(),
  getLocations()
]).then(([segments, locations]) => {

  window.locations = _.keyBy(locations, "tiploc");

  let i = 0;
  segments = _.sortBy(segments, "headcode");
  console.log(segments);

  plotSegment(segments[i]);

  // routeMap.time(new Date("Tue Mar 17 2015 11:38:00"));

  window.routeMap = routeMap;

  window.addEventListener("keydown", function(event) {
    if (event.keyCode == 37) {
      plotSegment(segments[--i]);
      event.preventDefault();
    } else if (event.keyCode == 39) {
      plotSegment(segments[++i]);
      event.preventDefault();
    }
  });

});

let reports = reportsContainer.append("g")
    .attr("class", "reports");

function plotSegment(segment) {
  console.log(`Plotting headcode:${segment.headcode || "_"} gps_car_id:${segment.gps_car_id || "_"}`, segment);
  let serviceStops = getServiceStopsFromSegment(segment);
  let unitStops = getUnitStopsFromSegment(segment);
  routeMap.plotServices([serviceStops]);
  routeMap.plotUnits([unitStops]);
  let scale = noOverlap()
      .minGap(12)
      .maxGap(50)
      .pixelsPerMinute(5)
      .build([serviceStops.map(d => d.event_time)]);
  reportsContainer.on("mousemove", () => {
    let p = d3.mouse(reportsContainer.node());
    routeMap.time(scale.invert(p[1]));
  });
  updateReports(reports, scale, serviceStops);
}

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

function getServiceStopsFromSegment(segment) {
  return _(segment.matching)
    .map(d => d.trust)
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

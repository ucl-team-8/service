import _ from "lodash";
import d3 from "d3";
import L from "leaflet";

import RouteMap from "./route-map";
import { getTrust, getGPS, getLocations } from "./data";

let transportLayer = new L.TileLayer("http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png")
    .setOpacity(0.25);

let map = new L.Map("map", {center: [53.5, -1.5], zoom: 7})
    .addLayer(transportLayer);

let routeMap = new RouteMap(map);

window.locations = {};

Promise.all([
  getTrust(),
  getGPS(),
  getLocations()
]).then(([trust, gps, locations]) => {

  window.locations = _.keyBy(locations, "tiploc");

  let services = d3.nest()
      .key(d => d.headcode)
      .sortValues((a, b) => d3.ascending(a.seq, b.seq))
      .entries(trust);

  let units = d3.nest()
      .key(d => d.gps_car_id)
      .sortKeys(d3.ascending)
      .sortValues((a,b) => d3.ascending(a.event_time, b.event_time))
      .entries(gps);

  routeMap.plotServices([services[30].values]);
  routeMap.plotUnits([units[26].values])

});

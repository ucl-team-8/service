import _ from "lodash";
import d3 from "d3";
import L from "leaflet";

import get from "./get";
import RouteMap from "./route-map";

let map = new L.Map("map", {center: [53.5, -1.5], zoom: 7})
    .addLayer(new L.TileLayer("http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png"));

let routeMap = new RouteMap(map);

import { getTrust, getGPS, getLocations } from "./data";

Promise.all([
  getTrust(),
  getGPS(),
  getLocations()
]).then(([trust, gps, locations]) => {
  locations = _.keyBy(locations, "tiploc");
  debugger;
});

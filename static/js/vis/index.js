import _ from "lodash";
import d3 from "d3";
import L from "leaflet";
import io from "socketio";

import {
  getSegment,
  getSegments,
  getLocations,
  parseSegment,
  parseMatching,
  serializeDate
} from "./utils/data";

import {
  getServiceKey,
  getServicesFromSegments,
  getSegmentsMatchingService
} from "./utils/segments";

import RouteMap from "./map/route-map";
import noOverlap from "./utils/no-overlap-time-scale";
import sameService from "./utils/same-service";
import renderSegments from "./reports/render";
import renderServices from "./services/render";

/*

IMPORTANT: All the code in this file is sort of hacked together and you probably
shouldn't add functionality here, instead make a new module or something.

*/

/* =============================================================================
   Globals
 */

window.render = render;
window.locations = {};
window.segments = [];
window.matchings = [];
window.selected;

/* =============================================================================
   Map
 */

let transportLayer = new L.TileLayer("http://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png")
    .setOpacity(0.15);

let map = new L.Map("map", {center: [53.5, -1.5], zoom: 7})
    .addLayer(transportLayer);

let routeMap = new RouteMap({ map });

window.routeMap = routeMap;


/* =============================================================================
   Rendering segments
 */

// getSegments().then(segments => {
//   window.segments = _.sortBy(segments, "headcode");
//   render();
// });

let segmentsContainer = d3.select(".segments-container");
let servicesContainer = d3.select(".services-container");

function render() {
  rerenderServices();
  rerenderSegments();
}

function rerenderServices() {
  let selected = window.selected;
  let segments = window.segments;
  // let services = getServicesFromSegments(segments);
  let services = window.matchings;
  services = _.sortBy(services, d => d.headcode);
  renderServices(servicesContainer.node(), services, selected);
}

function rerenderSegments() {
  let selected = window.selected;
  let serviceSegments = getSegmentsMatchingService(window.segments, selected);
  renderSegments(segmentsContainer.node(), serviceSegments, routeMap);
}

let socket = io();

/* =============================================================================
   Algorithm 2
 */

window.socket = socket;

socket.on('connect', function() {
  console.log("Connected");
  if (window.selected) subscribe(window.selected);
});

socket.on('locations', function(locations) {
  window.locations = _.keyBy(locations, "tiploc");
});

socket.on('matchings', function(matchings) {
  console.log("matchings update");
  window.matchings = matchings.map(parseMatching);
  rerenderServices()
});

socket.on('segments', function(segments) {
  console.log("segments update new");
  window.segments = segments.map(parseSegment);
  rerenderSegments();
});

socket.on('time', function(time) {
  console.log("time", time);
});

function subscribe(service) {
  let serviceKey = getServiceKey(service);
  serviceKey.origin_departure = serializeDate(serviceKey.origin_departure);
  socket.emit('subscribe', serviceKey);
}

window.select = (service) => {
  let serviceKey = getServiceKey(service);
  window.selected = serviceKey;
  console.log("selecting", serviceKey);
  subscribe(serviceKey);
  routeMap.plot([]);
  rerenderSegments();
}


/* =============================================================================
   Algorithm 1 - Socket segment synchronisation
 */

socket.on('update', function(data) {
  data = JSON.parse(data);
  let index = getSegmentWithId(data.id);
  if(index == -1) {
    // TODO: Segment with id was not found, something is broken
  } else {
    segments[index] = getSegment(data);
    let service = getServiceKey(segments[index]);
    if (_.isEqual(service, window.selected)) {
      rerenderSegments();
    }
  }
});

// The data is the id
socket.on('delete', function(data) {
  data = JSON.parse(data);
  let index = getSegmentWithId(data);
  if(index != -1) {
    let segment = segments.splice(index, 1)[0];
    let service = getServiceKey(segment);
    if (_.isEqual(service, window.selected)) {
      rerenderSegments();
    }
  }
});

socket.on('new', function(data) {
  data = JSON.parse(data);
  segments.push(getSegment(data));
});

function getSegmentWithId(id) {
  return _.findIndex(segments, d => d.id === id);
}

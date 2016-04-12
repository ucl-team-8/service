import _ from "lodash";
import d3 from "d3";
import L from "leaflet";
import io from "socketio";

import RouteMap from "./map/route-map";
import { getSegment, getSegments, getLocations } from "./utils/data";
import noOverlap from "./utils/no-overlap-time-scale";
import renderSegments from "./reports/render";
import renderServices from "./services/render";
import {
  getServiceFromSegment,
  getServicesFromSegments,
  getSegmentsMatchingService
} from "./utils/segments";

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

Promise.all([
  getSegments(),
  getLocations()
]).then(([segments, locations]) => {

  window.locations = _.keyBy(locations, "tiploc");
  window.segments = _.sortBy(segments, "headcode");

  render();

});

let segmentsContainer = d3.select(".segments-container");
let servicesContainer = d3.select(".services-container");

function render() {
  rerenderServices();
  rerenderSegments();
}

function rerenderServices() {
  let selected = window.selected;
  let segments = window.segments;
  let services = getServicesFromSegments(segments);
  services = _.sortBy(services, d => d.headcode);
  renderServices(servicesContainer.node(), services, selected);
}

function rerenderSegments() {
  let selected = window.selected;
  let serviceSegments = getSegmentsMatchingService(segments, selected);
  renderSegments(segmentsContainer.node(), serviceSegments, routeMap);
}


/* =============================================================================
   Socket segment synchronisation
 */

let socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
  console.log("Connected");
  socket.emit('connection', {data: 'I\'m connected!'});
});

socket.on('update', function(data) {
  data = JSON.parse(data);
  let index = getSegmentWithId(data.id);
  if(index == -1) {
    // TODO: Segment with id was not found, something is broken
  } else {
    segments[index] = getSegment(data);
    let service = getServiceFromSegment(segments[index]);
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
    let service = getServiceFromSegment(segment);
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

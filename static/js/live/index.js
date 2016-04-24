import _ from "lodash";
import d3 from "d3";
import L from "leaflet";
import io from "socketio";
import moment from "moment";

import {
  getSegment,
  getSegments,
  getLocations,
  parseSegment,
  parseMatching,
  parseDate,
  serializeDate,
  getServices,
  getUnits,
  getAugmented
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

import {
  getMatchingsFromAugmented,
  getSegmentsFromSelected
} from "./utils/static";


/* =============================================================================
   Globals
 */

window.render = render;
window.locations = {};
window.segments = [];
window.matchings = [];
window.selected;
window.service_search;


/* =============================================================================
   Static extract handling
 */

Promise.all([
  getServices(),
  getUnits(),
  getLocations(),
  getAugmented()
]).then(([services, units, locations, augmented]) => {
  window.services = services;
  window.units = units;
  window.matchings = getMatchingsFromAugmented(augmented);
  window.augmented = augmented;
  window.locations = _.keyBy(locations, "tiploc");
  render();
})



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
   Time
 */

let timeElem = d3.select(".current-time");
let timeFormat = date => moment(date).format("ddd, D MMM YYYY HH:mm");

window.updateTime = (time) => timeElem.text(timeFormat(time));

/* =============================================================================
   Service search
 */

let searchInput = d3.select(".service-search input");

searchInput.on("input", function() {
  serviceSearch(this.value);
});

function serviceSearch(query) {
  window.service_search = query;
  rerenderServices();
}

window.serviceSearchAndUpdate = function(query) {
  serviceSearch(query);
  searchInput.node().value = query;
};


/* =============================================================================
   Rendering segments
 */

// getSegments().then(segments => {
//   window.segments = _.sortBy(segments, "headcode");
//   render();
// });

let segmentsContainer = d3.select(".segments-container");
let servicesContainer = d3.select(".services-container .services");

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
  // let serviceSegments = getSegmentsMatchingService(window.segments, selected);
  let serviceSegments = getSegmentsFromSelected(selected);
  if (routeMap.isEmpty()) {
    let serviceSegment = _.find(serviceSegments, { type: "service" });
    if (serviceSegment) routeMap.plotServices([serviceSegment.trust]);
  }
  renderSegments(segmentsContainer.node(), serviceSegments, routeMap);
}

/* =============================================================================
   Algorithm 2
 */

// let socket = io();
//
// window.socket = socket;
//
// socket.on('connect', function() {
//   console.log("Connected");
//   if (window.selected) subscribe(window.selected);
// });
//
// socket.on('locations', function(locations) {
//   window.locations = _.keyBy(locations, "tiploc");
// });
//
// socket.on('matchings', function(matchings) {
//   console.log("matchings update");
//   console.log(matchings);
//   window.matchings = matchings.map(parseMatching);
//   rerenderServices()
// });
//
// socket.on('segments', function(segments) {
//   console.log("segments update new");
//   segments = window.segments = segments.map(parseSegment);
//   rerenderSegments();
//   if (routeMap.isEmpty()) {
//     let serviceSegment = _.find(segments, { type: "service" });
//     if (serviceSegment) routeMap.plotServices([serviceSegment.trust]);
//   }
// });
//
// socket.on('time', function(time) {
//   updateTime(parseDate(time));
// });
//
// function subscribe(service) {
//   let serviceKey = getServiceKey(service);
//   serviceKey.origin_departure = serializeDate(serviceKey.origin_departure);
//   socket.emit('subscribe', serviceKey);
// }
//
// function unsubscribe(service) {
//   let serviceKey = getServiceKey(service);
//   serviceKey.origin_departure = serializeDate(serviceKey.origin_departure);
//   socket.emit('unsubscribe', serviceKey);
// }

window.select = (service) => {

  // if (window.selected) {
  //   let oldServiceKey = getServiceKey(window.selected);
  //   unsubscribe(oldServiceKey);
  // }

  let serviceKey = getServiceKey(service);
  console.log("selecting", serviceKey);
  window.selected = serviceKey;
  // subscribe(serviceKey);
  routeMap.plot([]);
  render();
}


/* =============================================================================
   Algorithm 1 - Socket segment synchronisation
 */

// socket.on('update', function(data) {
//   data = JSON.parse(data);
//   let index = getSegmentWithId(data.id);
//   if(index == -1) {
//     // TODO: Segment with id was not found, something is broken
//   } else {
//     segments[index] = getSegment(data);
//     let service = getServiceKey(segments[index]);
//     if (_.isEqual(service, window.selected)) {
//       rerenderSegments();
//     }
//   }
// });
//
// // The data is the id
// socket.on('delete', function(data) {
//   data = JSON.parse(data);
//   let index = getSegmentWithId(data);
//   if(index != -1) {
//     let segment = segments.splice(index, 1)[0];
//     let service = getServiceKey(segment);
//     if (_.isEqual(service, window.selected)) {
//       rerenderSegments();
//     }
//   }
// });
//
// socket.on('new', function(data) {
//   data = JSON.parse(data);
//   segments.push(getSegment(data));
// });
//
// function getSegmentWithId(id) {
//   return _.findIndex(segments, d => d.id === id);
// }

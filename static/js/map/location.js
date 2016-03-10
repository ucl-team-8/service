import L from "leaflet";

export function tiplocToLocation(tiploc) {
  return window.locations[tiploc];
}

export function locationToPoint(map, { latitude, longitude }) {
  const latLng = new L.LatLng(latitude, longitude);
  return map.latLngToLayerPoint(latLng);
}

export function tiplocToPoint(map, tiploc) {
  return locationToPoint(map, tiplocToLocation(tiploc));
}

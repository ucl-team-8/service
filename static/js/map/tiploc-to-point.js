import L from "leaflet";

export default function tiplocToPoint(map, tiploc) {
  const { latitude, longitude } = window.locations[tiploc];
  const latLng = new L.LatLng(latitude, longitude);
  return map.latLngToLayerPoint(latLng);
}

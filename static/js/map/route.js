import d3 from "d3";

function sectionify(array) {
  let accumulator = [];
  for (let i = 0; i < array.length - 1; i++) {
    accumulator.push([array[i], array[i+1]]);
  }
  return accumulator;
}

export default class Route {

  constructor(map, container, data, type) {

    this.map = map;
    this.container = d3.select(container).append("g").attr("class", "route");

    this._appendStops(data);
    this._appendSections(sectionify(data));

    this.redraw();
  }

  stops() {
    return this.container.selectAll(".route-stop");
  }

  sectons() {
    return this.container.selectAll(".route-section");
  }

  latLngToPoint(lat, lng) {
    const latLng = new L.LatLng(lat, lng);
    return this.map.latLngToLayerPoint(latLng);
  }

  redraw() {

    let routeLine = d3.svg.line()
      .x(d => "")
      .y(d => "")

    this.stops()
      .attr("x", "")
      .attr("y", "")

    this.sections()
      .attr("d")
  }

  destroy() {
    this.container.remove();
  }

  _appendStops(stops) {
    this.stops().data(stops)
      .append("circle")
      .attr("class", "route-stop")
      .attr("r", 5);
  }

  _appendSections(sections) {
    this.sections().data(sections)
      .append("path")
      .attr("class", "route-section");
  }

}

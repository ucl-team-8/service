import d3 from "d3";

import tiplocToPoint from "./tiploc-to-point";

function sectionify(array) {
  let accumulator = [];
  for (let i = 0; i < array.length - 1; i++) {
    accumulator.push([array[i], array[i+1]]);
  }
  return accumulator;
}

function hasLocation(map, stop) {
  let location = window.locations[stop.tiploc];
  return !!(location && location.latitude != 0);
}

export default class Route {

  constructor(map, container, data, type) {

    this.map = map;
    this.container = container.append("g").attr("class", "route");
    this.data = data;

    if (type) {
      this.container.classed(type, true);
    }

    let stopsWithLocation = data.filter(d => hasLocation(this.map, d));

    this._appendSections(sectionify(stopsWithLocation));
    this._appendStops(stopsWithLocation);

    this.redraw();
  }

  stops() {
    return this.container.selectAll(".route-stop");
  }

  sections() {
    return this.container.selectAll(".route-section");
  }

  redraw() {

    let routeLine = d3.svg.line()
      .x(d => tiplocToPoint(this.map, d.tiploc).x)
      .y(d => tiplocToPoint(this.map, d.tiploc).y)

    this.stops()
      .attr("cx", d => tiplocToPoint(this.map, d.tiploc).x)
      .attr("cy", d => tiplocToPoint(this.map, d.tiploc).y)
      .attr("r", () => Math.pow(this.map.getZoom(), 2) / 18)

    this.sections()
      .attr("d", routeLine)
  }

  destroy() {
    this.container.remove();
  }

  _appendStops(stops) {
    this.stops()
      .data(stops)
    .enter()
      .append("circle")
      .attr("class", "route-stop");
  }

  _appendSections(sections) {
    this.sections()
      .data(sections)
    .enter()
      .append("path")
      .attr("class", "route-section");
  }

}

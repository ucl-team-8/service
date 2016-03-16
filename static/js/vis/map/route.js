import d3 from "d3";

import { tiplocToPoint, tiplocToLocation, tiplocHasLocation } from "../utils/location";
import sectionify from "../utils/sectionify";

export default class Route {

  constructor({ map, container, data, type }) {

    this.map = map;
    this.data = data;

    this.container = container.append("g").attr("class", "route");
    this.sectionsContainer = this.container.append("g");
    this.stopsContainer = this.container.append("g");

    this.progressLine = this.container.append("path")
      .attr("class", "route-section");

    this.time = null;

    if (type) {
      this.container.classed(type, true);
    }

    let stopsWithLocation = data.filter(d => tiplocHasLocation(d.tiploc));

    this.appendSections(sectionify(stopsWithLocation));
    this.appendStops(stopsWithLocation);

    this.redraw();
  }

  stops() {
    return this.stopsContainer.selectAll(".route-stop");
  }

  sections() {
    return this.sectionsContainer.selectAll(".route-section");
  }

  setTime(t) {
    this.time = t;
    this.redrawTime();
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

    this.redrawTime();
  }

  redrawTime() {
    let t = this.time;
    if (t) {

      this.stops()
        .classed("future", d => d.event_time > t);

      this.sections()
        .classed("future", d => d[1].event_time > t);

      this.showProgressLine();

      let sectionElem = this.sections()
        .filter(d => d[0].event_time <= t && d[1].event_time > t);

      let section = sectionElem.data()[0];

      if (section) {
        let start = section[0].event_time;
        let end = section[1].event_time;
        let progress = (t - start) / (end - start);
        let totalLength = sectionElem.node().getTotalLength();
        let startPos = sectionElem.node().getPointAtLength(0);
        let endPos = sectionElem.node().getPointAtLength(progress * totalLength);
        this.progressLine.attr("d", `M ${startPos.x}, ${startPos.y} L ${endPos.x}, ${endPos.y}`);
      } else {
        this.hideProgressLine();
      }

    } else {
      this.stops().classed("future", false);
      this.sections().classed("future", false);
      this.hideProgressLine();
    }
  }

  showProgressLine() {
    this.progressLine.style("display", null);
  }

  hideProgressLine() {
    this.progressLine.style("display", "none");
  }

  destroy() {
    this.container.remove();
  }

  appendStops(stops) {
    this.stops()
      .data(stops)
    .enter()
      .append("circle")
      .attr("class", "route-stop");
  }

  appendSections(sections) {
    this.sections()
      .data(sections)
    .enter()
      .append("path")
      .attr("class", "route-section");
  }

}

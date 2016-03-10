import _ from "lodash";
import d3 from "d3";

import { tiplocToPoint } from "./location";
import Route from "./route";

export default class RouteMap {

  constructor(map) {
    this.map = map;
    this.svg = d3.select(map.getPanes().overlayPane).append("svg").attr("width", 400).attr("height", 700);
    this.container = this.svg.append("g").attr("class", "leaflet-zoom-hide");

    this.unitsContainer = this.container.append("g")
        .attr("class", "units");

    this.servicesContainer = this.container.append("g")
        .attr("class", "services");

    this.units = [];
    this.services = [];

    this.redraw = this.redraw.bind(this);
    this.map.on("viewreset", this.redraw);
    this.redraw();
  }

  allRoutes() {
    return this.services.concat(this.units);
  }

  plotServices(services) {
    this.services.forEach(d => d.destroy());
    this.services = services.map(d => new Route(this.map, this.servicesContainer, d, "trust"));
    this.redraw();
  }

  plotUnits(units) {
    this.units.forEach(d => d.destroy());
    this.units = units.map(d => new Route(this.map, this.unitsContainer, d, "gps"));
    this.redraw();
  }

  time(t) {
    this.allRoutes().forEach(d => d.setTime(t));
  }

  redraw() {

    const allRoutes = this.allRoutes().map(d => d.data);
    const allLocations = _.flatten(allRoutes).map(d => tiplocToPoint(this.map, d.tiploc));

    if (allLocations.length) {
      const padding = 20;
      let [left, right] = d3.extent(allLocations, d => d.x);
      let [top, bottom] = d3.extent(allLocations, d => d.y);

      left   -= padding;
      right  += padding;
      top    -= padding;
      bottom += padding;

      this.svg
        .attr("width", right - left)
        .attr("height", bottom - top)
        .style("left", left + "px")
        .style("top", top + "px");

      this.container.attr("transform", "translate(" + -left + "," + -top + ")");
    }

    this.services.forEach(d => d.redraw());
    this.units.forEach(d => d.redraw());
  }

  destroy() {
    this.destroyContents();
    this.map.off("viewreset", this.redraw);
    this.container.remove();
  }

}

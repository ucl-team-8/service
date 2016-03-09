import d3 from "d3";

import Route from "./route";

export default class RouteMap {

  constructor(map) {
    this.map = map;
    this.svg = d3.select(map.getPanes().overlayPane).append("svg");
    this.container = this.svg.append("g").attr("class", "leaflet-zoom-hide");

    this.services = [];
    this.units = [];

    this.redraw = this.redraw.bind(this);
    this.map.on("viewreset", this.redraw);
  }

  plotServices(services) {
    this.services.forEach(d => d.destroy());
    this.services = services.map(d => new Route(d));
  }

  plotUnits(units) {
    this.units.forEach(d => d.destroy());
    this.units = units.map();
  }

  redraw() {
    this.services.forEach(d => d.redraw());
    this.units.forEach(d => d.redraw());
  }

  destroy() {
    this.destroyContents();
    this.map.off("viewreset", this.redraw);
    this.container.remove();
  }

}

import _ from "lodash";
import d3 from "d3";

import { tiplocToPoint, tiplocHasLocation } from "../utils/location";
import Route from "./route";

/*

Provides methods for plotting TRUST & GPS reports on a Leaflet.js map.

The Leaflet.js map should already exist and be passed as a parameter to the
constructor.

Much of the code is from https://bost.ocks.org/mike/leaflet/.

*/

export default class RouteMap {

  constructor({ map }) {

    this.map = map;

    this.svg = d3.select(map.getPanes().overlayPane)
      .append("svg")
      .attr("width", 400)
      .attr("height", 700);

    // The "leaflet-zoom-hide" class hides the plot during the zoom animation.
    this.container = this.svg.append("g")
      .attr("class", "leaflet-zoom-hide");

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

  /*
  Returns all `Route` instances that are plotted on the map.
  */
  allRoutes() {
    return this.services.concat(this.units);
  }

  /*

  Plots the given array of services on a map. A single service consists of an
  array of stops, e.g.

      var service = [
        { tiploc: "KNGX", event_time: ... },
        { tiploc: ..., event_time: ... }
      ];

  The logic for drawing routes is implemented in the `Route` class.
  */
  plotServices(services) {
    this.services.forEach(d => d.destroy());
    this.services = services.map(d => new Route({
      map: this.map,
      container: this.servicesContainer,
      data: d,
      type: "trust"
    }));
    this.redraw();
  }

  /*
  Plots the given array of units on a map. A single unit consists of an array of
  stops, just like a service (see above).
  */
  plotUnits(units) {
    this.units.forEach(d => d.destroy());
    this.units = units.map(d => new Route({
      map: this.map,
      container: this.unitsContainer,
      data: d,
      type: "gps"
    }));
    this.redraw();
  }

  /*
  */
  plot(items) {
    let [services, units] = _.partition(items, item => item.type == "trust")
    this.plotServices(services.map(d => d.reports));
    this.plotUnits(units.map(d => d.reports));
  }

  /*
  Given a Date object, it grays out all the stops that happened in the future.
  Pass `null` to reset.
  */
  time(t) {
    this.allRoutes().forEach(d => d.setTime(t));
  }

  /*
  Redraws the all routes. This method is called automatically in case of updated
  services, or on map zoom.
  */
  redraw() {

    const allRoutes = this.allRoutes().map(d => d.data);
    const allLocations = _.flatten(allRoutes)
      .filter(d => tiplocHasLocation(d.tiploc))
      .map(d => tiplocToPoint(this.map, d.tiploc));

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

  /*
  Removes all the plots, as well as container elements used for drawing.
  After executing this, the instance is unusable and you need to create a new
  one if you want to continue plotting.
  */
  destroy() {
    this.allRoutes().forEach(d => d.destroy());
    this.map.off("viewreset", this.redraw);
    this.svg.remove();
  }

  isEmpty() {
    return this.units.length === 0 && this.services.length === 0;
  }

}

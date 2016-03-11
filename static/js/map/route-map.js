import _ from "lodash";
import d3 from "d3";

import { tiplocToPoint } from "./location";
import Route from "./route";

/*

Provides methods for plotting TRUST & GPS reports on a Leaflet.js map.

The Leaflet.js map should already exist and be passed as a parameter to the
constructor.

Much of the code is from https://bost.ocks.org/mike/leaflet/.

*/

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

  /*
  Returns all Route objects that are plotted on the map.
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

  */
  plotServices(services) {
    this.services.forEach(d => d.destroy());
    this.services = services.map(d => new Route(this.map, this.servicesContainer, d, "trust"));
    this.redraw();
  }

  /*
  Plots the given array of units on a map. A single unit consists of an array of
  stops, just like a service (see above).
  */
  plotUnits(units) {
    this.units.forEach(d => d.destroy());
    this.units = units.map(d => new Route(this.map, this.unitsContainer, d, "gps"));
    this.redraw();
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
  services, or an action like zoom.
  */
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

  /*
  Removes all the plots, as well as container elements used for drawing.
  After executing this, the instance is unusable and you need to create a new
  one if you want to continue plotting.
  */
  destroy() {
    this.destroyContents();
    this.map.off("viewreset", this.redraw);
    this.container.remove();
  }

}

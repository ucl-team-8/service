import d3 from "d3";
import renderSegment from "./render-segment";
import {
  getUnitStopsFromSegment,
  getServiceStopsFromSegment,
  getScaleFromSegments
} from "../utils/segments";


export default function render(container, segments, routeMap) {

  container = d3.select(container);

  let segmentContainers = container.selectAll(".segment")
      .data(segments);

  let newSegConts = segmentContainers.enter()
    .append("div")
      .attr("class", "segment");

  newSegConts.append("div")
      .attr("class", "header")
      .text(d => d.gps_car_id);

  newSegConts.append("svg").append("g");

  segmentContainers.exit().remove();


  let scale = getScaleFromSegments(segments);

  window.scale = scale;

  segmentContainers.each(function(segment) {
    let trust = getServiceStopsFromSegment(segment);
    let gps = getUnitStopsFromSegment(segment);
    let data = [{
      type: "trust",
      reports: trust
    }, {
      type: "gps",
      reports: gps
    }];
    renderSegment(this, scale, data, routeMap);
  });

}

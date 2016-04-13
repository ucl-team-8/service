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

  segmentContainers.each(function(segment) {
    let data = [];
    if (segment.trust && segment.trust.length) {
      data.push({
        type: "trust",
        reports: segment.trust
      });
    }
    if (segment.gps && segment.gps.length) {
      data.push({
        type: "gps",
        reports: segment.gps
      });
    }
    renderSegment(this, scale, data, routeMap);
  });

}

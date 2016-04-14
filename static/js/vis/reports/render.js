import d3 from "d3";
import renderSegment from "./render-segment";
import {
  getUnitStopsFromSegment,
  getServiceStopsFromSegment,
  getScaleFromSegments
} from "../utils/segments";

const TEXT = {
  service: "All reports for the service selected.",
  added: "<b class='matched'>Matched</b> but <b>wasn't planned</b>",
  unchanged: "<b class='matched'>Matched</b> and was <b>planned</b>",
  removed: "<b>Planned</b>, but <b class='not-matched'>didn't match</b>",
  no_data: "<b>Planned</b>, but there is <b class='insufficient-data'>insufficient data</b>"
}

export default function render(container, segments, routeMap) {

  container = d3.select(container);

  let segmentContainers = container.selectAll(".segment")
      .data(segments);

  // enter

  let newSegConts = segmentContainers.enter().append("div")
      .attr("class", "segment");

  newSegConts.append("div")
      .attr("class", "header");

  newSegConts.append("svg").append("g");

  segmentContainers.exit().remove();

  segmentContainers.attr("class", d => `segment type-${d.type || ""}`);

  let header = segmentContainers.select(".header").html("");

  header.append("div")
      .attr("class", "heading")
    .append("span")
      .text(d => d.type === "service" ? d.headcode : d.gps_car_id)
      .on("click", d => {
        if (d.type !== "service") window.serviceSearchAndUpdate(d.gps_car_id);
      });

  header.append("div")
      .attr("class", "explanation")
      .html(d => TEXT[d.type]);

  // rendering reports

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

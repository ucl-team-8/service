import d3 from "d3";
import noOverlap from "../utils/no-overlap-time-scale";

export default function updateReports(container, scale, data) {

  let a;

  let reports = container.selectAll(".report")
      .data(scale.positions(data, d => d.event_time));

  reports.enter()
    .append("g")
      .attr("class", "report")
      .attr("transform", d => `translate(0, ${d.pos})`)
    .append("circle")
      .attr("cx", 50)
      .attr("cy", 0)
      .attr("r", 5);

  reports.exit()
    .remove();

  // let stops = unitDiagram.selectAll(".stop")
  //     .data(noOverlapY.positions(unit.values, d => d.event_time))
  //   .enter().append("g")
  //     .attr("class", "stop")
  //     .attr("transform", d => `translate(0, ${d.pos})`);

  // stops.append("circle")
  //     .attr("cx", 100)
  //     .attr("cy", 0)
  //     .attr("r", radius);

  // let labels = stops.append("text")
  //     .attr("y", 0)
  //     .attr("x", 100 + 8)
  //     .attr("dy", ".35em");
  //
  // labels.append("tspan")
  //     .attr("class", "event_type")
  //     .text(d => d.event_type);
  //
  // labels.append("tspan")
  //     .attr("class", "tiploc")
  //     .text(d => " " + d.tiploc);
  //
  // stops.append("text")
  //     .attr("class", "time")
  //     .attr("y", 0)
  //     .attr("x", 100 - 8)
  //     .attr("dy", ".35em")
  //     .text(d => timeFormat(d.event_time));
}

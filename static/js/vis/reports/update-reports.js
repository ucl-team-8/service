import d3 from "d3";
import noOverlap from "../utils/no-overlap-time-scale";

export default function updateReports(container, scale, data) {

  let timeFormat = d3.time.format("%H:%M:%S");

  let dataWithPositions = scale.positions(data, d => d.event_time);

  let reports = container.selectAll(".report")
      .data(dataWithPositions, d => d.id);

  let newReports = reports.enter()
    .append("g")
      .attr("class", "report");

  newReports.append("circle")
      .attr("cx", 100)
      .attr("cy", 0)
      .attr("r", 4);

  let newLabels = newReports.append("text")
      .attr("y", 0)
      .attr("x", 100 + 8)
      .attr("dy", ".35em");

  newLabels.append("tspan")
      .attr("class", "event-type")
      .text(d => d.event_type);

  newLabels.append("tspan")
      .attr("class", "tiploc")
      .text(d => " " + d.tiploc);

  newReports.append("text")
      .attr("class", "time")
      .attr("y", 0)
      .attr("x", 100 - 8)
      .attr("dy", ".35em")
      .text(d => timeFormat(d.event_time));

  reports.exit()
    .remove();

  reports.attr("transform", d => `translate(0, ${d.pos})`);

}

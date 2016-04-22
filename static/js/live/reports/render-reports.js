import d3 from "d3";

export default function renderReports(container, scale, data) {

  container = d3.select(container);

  let leftOffset = 40;
  let timeFormat = d3.time.format("%H:%M");
  let dataWithPositions = scale.positions(data, d => d.event_time);

  // Drawing the bar

  let positions = dataWithPositions.map(d => d.pos);
  let top = d3.min(positions);
  let bottom = d3.max(positions);

  let bar = container.select(".bar");

  if (bar.empty()) {
      bar = container.append("line")
        .attr("class", "bar");
  }

  bar.attr("x1", leftOffset)
    .attr("x2", leftOffset)
    .attr("y1", top)
    .attr("y2", bottom);

  // Drawing the reports (circles)

  let reports = container.selectAll(".report")
      .data(dataWithPositions, d => d.id);

  let newReports = reports.enter()
    .append("g")
      .attr("class", "report");

  newReports.append("circle")
      .attr("cx", leftOffset)
      .attr("cy", 0)
      .attr("r", 4);

  let newLabels = newReports.append("text")
      .attr("y", 0)
      .attr("x", leftOffset + 8)
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
      .attr("x", leftOffset - 8)
      .attr("dy", ".35em")
      .text(d => timeFormat(d.event_time));

  reports.exit()
    .remove();

  reports.attr("transform", d => `translate(0, ${d.pos})`);

}

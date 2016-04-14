import d3 from "d3";
import renderReports from "./render-reports";

let widthOfItem = 120;
let padding = { top: 20, bottom: 30, left: 25, right: 20 };

export default function renderSegment(container, scale, data, routeMap) {

  container = d3.select(container);

  data = _.orderBy(data, segment => [
    segment.type == "service",
    segment.type == "added",
    segment.type == "removed"
  ], ["desc", "desc", "desc"]);

  let width = data.length * widthOfItem + padding.left + padding.right;
  let height = d3.max(scale.range()) + padding.top + padding.bottom;

  let svg = container.select("svg")
      .attr("width", width)
      .attr("height", height);

  let g = svg.select("g")
      .attr("transform", `translate(${padding.left}, ${padding.top})`)
      .attr("class", "container");

  let plots = g.selectAll(".reports").data(data);

  plots.enter().append("g")
      .attr("class", d => `reports ${d.type || ""}`);


  plots.exit().remove();

  plots.attr("transform", (d,i) => `translate(${ widthOfItem * i }, 0)`)
      .each(function(data) { renderReports(this, scale, data.reports) });

  svg.on("mouseenter", () => routeMap.plot(data))
    .on("mousemove", () => {
      let p = d3.mouse(svg.node());
      routeMap.time(scale.invert(p[1] - padding.top));
    });


}

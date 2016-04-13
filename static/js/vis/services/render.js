import d3 from "d3";
import moment from "moment";

export default function render(container, data, selected) {

  container = d3.select(container);

  let services = container.selectAll(".service").data(data);

  services.enter().append("div")
      .attr("class", "service");

  services.html(d => d.headcode != null ? template(d) : noServiceTemplate(d))
      .classed("selected", d => _.isEqual(d, selected))
      .on("click", d => {
        window.selected = d;
        window.render();
      });

}

function formatDate(date) {
  return moment(date).format("HH:mm");
}

let template = (d) => `
  <div class="metadata">
    <div class="departure">
      <span class="time">${formatDate(d.origin_departure)}</span>
      <span class="origin">${d.origin_location}</span>
    </div>
    <h3>
      <span class="headcode">${d.headcode}</span>
    </h3>
  </div>
  <!--<div class="matchings">
    <span>${d.count || ""}</span>
  </div>-->`

let noServiceTemplate = (d) => `
  <div class="metadata">
    <div class="departure">
      <span class="time"></span>
      <span class="origin"></span>
    </div>
    <h3>
      <span class="headcode">Without service</span>
    </h3>
  </div>`

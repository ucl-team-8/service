import d3 from "d3";
import moment from "moment";
import sameService from "../utils/same-service";

export default function render(container, data, selected) {

  container = d3.select(container);

  data = _.sortBy(data, service => [!(service.units.added || service.units.removed), service.headcode]);

  let services = container.selectAll(".service").data(data);

  services.enter().append("div")
      .attr("class", "service");

  services.html(d => d.headcode != null ? template(d) : noServiceTemplate(d))
      .classed("selected", d => sameService(d, window.selected))
      .on("click", d => {
        window.select(d);
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
  <div class="matchings">
    ${matchingsTemplate(d.units)}
  </div>`

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


let matchingsTemplate = (d) => {
  let tmp = "";
  if (d.added) tmp += `<span class="added">${d.added.length}</span>`;
  if (d.unchanged) tmp += `<span class="unchanged">${d.unchanged.length}</span>`;
  if (d.removed) tmp += `<span class="removed">${d.removed.length}</span>`;
  return tmp;
}

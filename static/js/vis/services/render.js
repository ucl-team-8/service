import d3 from "d3";
import moment from "moment";
import sameService from "../utils/same-service";

export default function render(container, data, selected) {

  container = d3.select(container);

  data = _.sortBy(data, service => [!(service.units.added || service.units.removed), service.headcode]);

  if (window.service_search) {
    let q = window.service_search.toLowerCase();
    data = data.filter(matching => {
      let keywords = extractKeywords(matching);
      return _.some(keywords, keyword => keyword.indexOf(q) > -1);
    });
  }

  let services = container.selectAll(".service").data(data);

  services.enter().append("div")
      .attr("class", "service");

  services.exit().remove()

  services.html(d => d.headcode != null ? template(d) : noServiceTemplate(d))
      .classed("selected", d => sameService(d, window.selected))
      .on("click", d => {
        window.select(d);
      });

}

function extractKeywords(matching) {
  let units = _.flatten(_.values(matching.units));
  let unit_types = _.flatten(_.keys(matching.units));
  let keywords = [
    matching.headcode,
    matching.origin_location
  ].concat(units).concat(unit_types);
  return keywords.map(k => k.toLowerCase());
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
  // combine no_data and unchanged in the same "unchanged" field
  let no_data = d.no_data ? d.no_data.length : 0;
  let unchanged = d.unchanged ? d.unchanged.length : 0;
  let count = no_data + unchanged;

  if (d.added) tmp += `<span class="added">${d.added.length}</span>`;
  if (count) tmp += `<span class="unchanged">${count}</span>`;
  if (d.removed) tmp += `<span class="removed">${d.removed.length}</span>`;

  return tmp;
}

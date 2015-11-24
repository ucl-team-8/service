import d3 from "d3";
import _ from "lodash";
import moment from "moment";

d3.json("/events/trust.json", function(err, { result: trustData }) {
  d3.json("/events/gps.json", function(err, { result: gpsData }) {

    if (err) console.error(err);

    trustData.forEach(trustDatatypes);
    gpsData.forEach(gpsDatatypes);

    let services = d3.nest()
        .key(d => d.gps_car_id).sortKeys(d3.ascending)
        .key(d => d.CIF_uid).sortKeys(d3.ascending)
        .sortValues((a, b) => d3.ascending(a.loc_seq, b.loc_seq))
        .entries(trustData);

    let units = d3.nest()
        .key(d => d.gps_car_id)
        .sortKeys(d3.ascending)
        .entries(gpsData);

    let unit = units[2];

    let width = 200;
    let height = 800;

    let y = d3.time.scale()
        .domain(d3.extent(unit.values, d => d.event_time))
        .range([0, height])
        .nice();

    let svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("class", "unit-diagram");

    let stops = svg.selectAll("circle")
        .data(unit.values)
      .enter()
        .append("circle")
        .attr("class", "stop")
        .attr("cx", width / 2)
        .attr("cy", d => y(d.event_time))
        .attr("r", 4)

    // debugger;

    console.log(unit);
  });
});

function trustDatatypes(d) {
  if (d.dep_report) d.dep_report = new Date(d.dep_report);
  if (d.arrival_report) d.arrival_report = new Date(d.arrival_report);
  d.origin_depart_time = new Date(d.origin_depart_time);
  d.location = d.location.trim(); // TODO: trim this in import
}

function gpsDatatypes(d) {
  d.event_time         = new Date(d.event_time);
}

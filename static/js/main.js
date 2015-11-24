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
        .key(d => d.CIF_uid)
        .sortValues((a, b) => d3.ascending(a.loc_seq, b.loc_seq))
        .entries(trustData);

    let units = d3.nest()
        .key(d => d.gps_car_id)
        .sortKeys(d3.ascending)
        .entries(gpsData);

    let unit = units[52];
    let unitServices = _.find(services, d => d.key == unit.key).values;

    console.log(unitServices);

    let timeFormat = d3.time.format("%H:%M");
    let stopNames = unit.values.map(d => d.tiploc);

    let width = 200;
    let height = stopNames.length * 18;

    let y = d3.scale.ordinal()
        .domain(d3.range(stopNames.length))
        .rangeRoundBands([0, height], .1);

    let scaleY = (d,i) => y(i)

    let svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("class", "unit-diagram");

    let stops = svg.selectAll(".stop")
        .data(unit.values)
      .enter().append("g")
        .attr("class", "stop");

    stops.append("circle")
        .attr("cx", width / 2)
        .attr("cy", scaleY)
        .attr("r", 4);

    let labels = stops.append("text")
        .attr("y", scaleY)
        .attr("x", width / 2 + 8)
        .attr("dy", ".35em");

    labels.append("tspan")
        .attr("class", "event_type")
        .text(d => d.event_type);

    labels.append("tspan")
        .attr("class", "tiploc")
        .text(d => " " + d.tiploc);

    stops.append("text")
        .attr("class", "time")
        .attr("y", scaleY)
        .attr("x", width / 2 - 8)
        .attr("dy", ".35em")
        .text(d => timeFormat(d.event_time));

    let service = unitServices[0];

    // debugger;

    // function(gpsStops, trustStop) => index of station

    function getIndexOfStop(unitStops, serviceStop) {

    }

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
  d.event_time = new Date(d.event_time);
}

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
        .key(d => d.headcode)
        .sortValues((a, b) => d3.ascending(a.seq, b.seq))
        .entries(trustData);

    let units = d3.nest()
        .key(d => d.gps_car_id)
        .sortKeys(d3.ascending)
        .sortValues((a,b) => d3.ascending(a.event_time, b.event_time))
        .entries(gpsData);

    let unit = units[52];
    let unitServices = _.find(services, d => d.key == unit.key).values;

    console.log(unitServices);

    let timeFormat = d3.time.format("%H:%M:%S");
    let totalUnitStops = unit.values.length;

    let width = 600;
    let height = totalUnitStops * 18;

    let y = d3.scale.ordinal()
        .domain(d3.range(totalUnitStops))
        .rangeRoundBands([0, height], .1);

    let scaleY = (d,i) => y(i)

    let svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    let unitDiagram = svg.append("g")
        .attr("class", "unit-diagram")
        .attr("transform", "translate(0,0)");

    let stops = unitDiagram.selectAll(".stop")
        .data(unit.values)
      .enter().append("g")
        .attr("class", "stop");

    stops.append("circle")
        .attr("cx", 100)
        .attr("cy", scaleY)
        .attr("r", radius);

    let labels = stops.append("text")
        .attr("y", scaleY)
        .attr("x", 100 + 8)
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
        .attr("x", 100 - 8)
        .attr("dy", ".35em")
        .text(d => timeFormat(d.event_time));

    let indexFromTime = d3.scale.quantile()
        .domain(unit.values.map(d => d.event_time))
        .range(d3.range(totalUnitStops));

    function getIndexOfStop(d) {
      try {
        // return indexFromTime(d.event_time);
        let m = match(unit.values, d);
        return unit.values.indexOf(m);
      } catch(e) {
        console.log("Could not detect time for:", d);
      }
    }

    function radius(d) {
      if (d.event_type == "A" || d.event_type == "D") {
        return 4;
      } else {
        return 1;
      }
    }

    function matches(trustEvent) {
      let gpsEvent = unit.values[getIndexOfStop(trustEvent)];
      return gpsEvent.tiploc == trustEvent.tiploc;
    }

    let mergedServices = _.flatten(unitServices.map(d => d.values));

    let serviceDiagram = svg.append("g")
        .attr("class", "service-diagram")
        .attr("transform", "translate(150,0)");

    let serviceStops = serviceDiagram.selectAll(".stop")
        .data(mergedServices)
      .enter().append("g")
        .attr("class", "stop");

    serviceStops.append("circle")
        .attr("class", d => {
          return matches(d) ? "good" : "bad";
        })
        .attr("cx", 100)
        .attr("cy", d => y(getIndexOfStop(d)))
        .attr("r", radius)
        .style("fill", d => {
          // check if the two match
          return "none";
        });

    serviceStops.append("text")
        .attr("class", "time")
        .attr("y", d => y(getIndexOfStop(d)))
        .attr("x", 100 - 8)
        .attr("dy", ".35em")
        .text(d => timeFormat(d.event_time));

    let serviceLabels = serviceStops.append("text")
        .attr("y", d => y(getIndexOfStop(d)))
        .attr("x", 100 + 8)
        .attr("dy", ".35em");

    serviceLabels.append("tspan")
        .attr("class", "event_type")
        .text(d => d.event_type);

    serviceLabels.append("tspan")
        .attr("class", "tiploc")
        .text(d => " " + d.tiploc);

    match(unit.values, mergedServices[10]);

    console.log(unit);
  });
});

function findAbsTimeDifference(eventA, eventB) {
  let diff = (new Date(eventA.event_time)) - (new Date(eventB.event_time));
  return Math.abs(diff);
}

function match(gpsEvents, trustEvent) {
  let tolerance = 10 * 60 * 1000;
  // let closest = _.sortByOrder(gpsEvents, [gpsEvent => findAbsTimeDifference(gpsEvent, trustEvent), "event_type"], ["asc", "asc"]);
  let closest = gpsEvents.filter(event => findAbsTimeDifference(event, trustEvent) < tolerance);
  let sameStop = closest.filter(event => event.tiploc == trustEvent.tiploc);
  let sameType = _.findWhere(sameStop, { event_type: trustEvent.event_type });
  if (sameType) {
    return sameType;
  } else if (sameStop.length > 0) {
    return sameStop[0];
  } else {
    console.error("Couldn't match:", trustEvent.tiploc, trustEvent.event_time, trustEvent);
    return _.sortBy(closest, event => findAbsTimeDifference(event, trustEvent))[0];
  }
}

function trustDatatypes(d) {
  d.event_time = new Date(d.event_time);
  d.origin_depart_time = new Date(d.origin_departure);
  d.tiploc = d.tiploc.trim(); // TODO: trim this in import
}

function gpsDatatypes(d) {
  d.event_time = new Date(d.event_time);
}

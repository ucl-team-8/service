import d3 from "d3";
import _ from "lodash";
import noOverlap from "./no-overlap";

let notMatched = [];
var data = window.data || {};

let index = 0;
var selectElement = document.getElementById("select_unit");
selectElement.onchange = function() {
  index = parseInt(this.value);
  // Remove all list elements
  while(this.firstChild) {
    this.removeChild(this.firstChild);
  }
  // Remove svg
  var svg = document.getElementById("visualisation_svg");
  svg.parentNode.removeChild(svg);

  draw();
};
draw();


function loadData() {
  return new Promise((resolve, reject) => {

    if (data && data.trustData) return resolve(data);

    d3.json("/events/trust.json", function(err, { result: trustData }) {
      d3.json("/events/gps.json", function(err, { result: gpsData }) {
        data.trustData = trustData;
        data.gpsData = gpsData;
        return resolve(data);
      });
    });

  });
}

function draw() {

  loadData().then(function({trustData, gpsData}) {
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

    let unitChoice = d3.select("#select_unit");

    for(var i = 0; i < units.length; i++) {
      let choice = unitChoice.append("option")
        .attr("value", i)
        .text(units[i].key);
      if(i == index) {
        choice.attr("selected", "selected");
      }
    }

    let unit = units[index];
    let unitServices;

    try {
      unitServices = _.find(services, d => d.key == unit.key).values;
    } catch(e) {
      console.error(e);
      return;
    }

    console.log(unitServices);

    let timeFormat = d3.time.format("%H:%M:%S");
    let totalUnitStops = unit.values.length;

    let width = 600;
    let height = totalUnitStops * 60;

    let y = d3.time.scale()
        .domain(d3.extent(unit.values, d => d.event_time))
        .range([0, height]);

    let collectionsOfTimes = _.union(
      [unit.values.map(d => d.event_time)],
      unitServices.map(d => d.values.map(d => d.event_time))
    );

    let noOverlapY = noOverlap()
        .minGap(12)
        .maxGap(50)
        .pixelsPerMinute(5)
        .build(collectionsOfTimes);

    // let scaleY = (d,i) => y(d.event_time);

    let svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("id", "visualisation_svg");

    let unitDiagram = svg.append("g")
        .attr("class", "unit-diagram")
        .attr("transform", "translate(0,0)");

    let stops = unitDiagram.selectAll(".stop")
        .data(noOverlapY.positions(unit.values, d => d.event_time))
      .enter().append("g")
        .attr("class", "stop")
        .attr("transform", d => `translate(0, ${d.pos})`);

    stops.append("circle")
        .attr("cx", 100)
        .attr("cy", 0)
        .attr("r", radius);

    let labels = stops.append("text")
        .attr("y", 0)
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
        .attr("y", 0)
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
      try {
        return gpsEvent.tiploc == trustEvent.tiploc;
      }
      catch(e) {
        return false;
      }
    }

    let mergedServices = _.flatten(unitServices.map(d => d.values));

    let serviceDiagram = svg.append("g")
        .attr("class", "service-diagram")
        .attr("transform", "translate(150,0)");

    let serviceStops = serviceDiagram.selectAll(".stop")
        .data(noOverlapY.positions(mergedServices, d => d.event_time))
      .enter().append("g")
        .attr("class", "stop")
        .attr("transform", d => `translate(0, ${d.pos})`);

    serviceStops.append("circle")
        .attr("class", d => {
          return matches(d) ? "good" : "bad";
        })
        .attr("cx", 100)
        .attr("cy", 0)
        .attr("r", radius)
        .style("fill", d => {
          // check if the two match
          return "none";
        });

    serviceStops.append("text")
        .attr("class", "time")
        .attr("y", 0)
        .attr("x", 100 - 8)
        .attr("dy", ".35em")
        .text(d => timeFormat(d.event_time));

    let serviceLabels = serviceStops.append("text")
        .attr("y", 0)
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
    console.log("Couldn't match:", _.uniq(notMatched));
  });

}

function findAbsTimeDifference(eventA, eventB) {
  let diff = (new Date(eventA.event_time)) - (new Date(eventB.event_time));
  return Math.abs(diff);
}

function match(gpsEvents, trustEvent) {
  // 10 Minutes
  let tolerance = 10 * 60 * 1000;
  // let closest = _.sortByOrder(gpsEvents, [gpsEvent => findAbsTimeDifference(gpsEvent, trustEvent), "event_type"], ["asc", "asc"]);
  let closest = gpsEvents.filter(event => findAbsTimeDifference(event, trustEvent) < tolerance);
  let sameStop = closest.filter(event => event.tiploc == trustEvent.tiploc);
  let sameType = _.find(sameStop, { event_type: trustEvent.event_type });
  if (sameType) {
    return sameType;
  } else if (sameStop.length > 0) {
    return sameStop[0];
  } else {
    notMatched.push(trustEvent);
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

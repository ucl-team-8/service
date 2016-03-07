import d3 from "d3";
import _ from "lodash";

let notMatched = [];
var data = window.data || {};

let index = 0;
var selectElement = document.getElementById("select_unit");
selectElement.onchange = function() {
  index = parseInt(this.value);
  while(this.firstChild) {
    this.removeChild(this.firstChild);
  }
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
        .key(d => d.headcode)
        .sortKeys(d3.ascending)
        .sortValues((a,b) => d3.ascending(a.event_time, b.event_time))
        .entries(trustData);

    let units = d3.nest()
        .key(d => d.gps_car_id)
        .sortKeys(d3.ascending)
        .sortValues((a,b) => d3.ascending(a.event_time, b.event_time))
        .entries(gpsData);

    let unit = units[index];
    matchingAlgorithm(unit, services);
    services
      .sort((a, b) => (a.probability - b.probability) !== 0 ? d3.descending(a.probability, b.probability)
       : d3.descending(a.values[0].gps_car_id == unit.key, b.values[0].gps_car_id == unit.key));

    let timeFormat = d3.time.format("%H:%M:%S");
    let totalUnitStops = unit.values.length;
    let totalServices = services.length;

    let width = 150 * (totalServices + 2);
    let height = totalUnitStops * 18;

    let y = d3.scale.ordinal()
    .domain(d3.range(totalUnitStops))
    .rangeRoundBands([0, height], 0.1);

    let scaleY = (d,i) => y(i);

    console.log(units);
    let unitChoice = d3.select("#select_unit");

    for(var i = 0; i < units.length; i++) {
      let choice = unitChoice.append("option")
        .attr("value", i)
        .text(units[i].key);
      if(i == index) {
        choice.attr("selected", "selected");
      }
    }

    let svg = d3.select("body").append("svg")
      .attr("id", "visualisation_svg")
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
      .attr("cy", (d,i) => y(i))
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
        let m = match(unit.values, d, false);
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

    for(var i = 0; i < services.length; i++) {
      let serviceDiagram = svg.append("g")
          .attr("class", "service-diagram")
          .attr("transform", "translate(" + 150 * (i + 1) + ",0)");

      let heading = serviceDiagram.append("g")
        .attr("class", "header");

      let headingText = heading.append("text")
        .attr("y", 50)
        .attr("x", 50)
        .attr("class", services[i].values[0].gps_car_id == unit.key ? "good" : "bad")
        .text(services[i].key + " " + (services[i].probability * 100).toFixed(2) + "%");

      let serviceStops = serviceDiagram.selectAll(".stop")
          .data(services[i].values)
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

      console.log("Couldn't match for service " + services[i].key +
       ":", _.uniq(notMatched));
      notMatched = [];
    }

  });



}

function trustDatatypes(d) {
  d.event_time = new Date(d.event_time);
  d.origin_depart_time = new Date(d.origin_departure);
  d.tiploc = d.tiploc.trim();
}

function gpsDatatypes(d) {
  d.event_time = new Date(d.event_time);
}

function findAbsTimeDifference(eventA, eventB) {
  let diff = (new Date(eventA.event_time)) - (new Date(eventB.event_time));
  return Math.abs(diff);
}

function match(gpsEvents, trustEvent, usingAlgorithm) {
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
    if(!usingAlgorithm) {
      notMatched.push(trustEvent);
      return _.sortBy(closest, event => findAbsTimeDifference(event, trustEvent))[0];
    }
    return null;
  }
}


function matchingAlgorithm(unit, services) {
  for(var i = 0; i < services.length; i++) {
    let serviceValues = services[i].values;
    let serviceLength = serviceValues.length;
    let serviceMatched = 0;
    for(var j = 0; j < serviceLength; j++) {
      let matchingUnit = match(unit.values, serviceValues[j], true);
      if(matchingUnit !== null) {
        serviceMatched++;
      }
    }
    services[i].probability = serviceMatched/serviceLength;
    if(services[i].probability < 0.5) {
      services.splice(i, 1);
      i--;
    }
  }
}

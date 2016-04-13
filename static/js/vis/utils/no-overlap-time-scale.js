import _ from "lodash";
import d3 from "d3";
import moment from "moment";
import sectionify from "./sectionify";


/*

The way this scale avoids overlapping is by stretching time between points that
overlap. It does this by creating a polylinear D3 time scale (which is basically
just multiple linear time scales joined together, each one acting in a specific
domain.)

What follows below is a huge mess of code to construct this polylinear scale.

*/

// Pair up consecutive events, calculate and store properties of each pair.
// The return result is considered a "scale".
function calcScales(minPixelsPerMinute, minGap, maxGap, events) {
  if (events.length == 0) return [];
  if (events.length == 1) return [{
    domain: [events[0], events[0]],
    pixelsPerMinute: Infinity
  }];
  return sectionify(events).map(([a,b]) => {
    let minutes = (b - a) / (1000 * 60);
    let min = (minGap == 0) ? 0 : minGap / minutes;
    let max = (maxGap == Infinity) ? Infinity : maxGap / minutes;
    // pixelsPerMinute is Infinity when the two events happened at the exact same time
    let pixelsPerMinute = Math.min(Math.max(min, minPixelsPerMinute), max);
    return {
      domain: [a, b],
      pixelsPerMinute
    };
  });
}

// Gets all the domain ends/starts that occur in a list of scales.
function getAllPoints(scales) {
  return _.chain(scales)
    .map(d => d.domain)
    .flatten()
    .value();
}

function getNextStop(time, scales) {
  return _.chain(getAllPoints(scales))
    .filter(d => d > time)
    .min()
    .value();
}

function getDomainStart(scales) {
  return _.chain(getAllPoints(scales))
    .min()
    .value();
}

function scaleCovers(domain, scale) {
  return domain[0] >= scale.domain[0] && domain[1] <= scale.domain[1];
}

function getScalesCovering(domain, scales) {
  return scales.filter(scale => scaleCovers(domain, scale));
}

function getMaxAtSameTime(time, scales) {
  let candidates = scales.filter(scale => _.isEqual(scale.domain, [time, time]));
  return _.maxBy(candidates, d => d.numberOfEvents);
}

function combineScales(defaultPixelsPerMinute, collections) {
  let output = [];
  let scales = _.flatten(collections);
  if (scales.length == 0) return output;
  if (scales.length == 1) return scales;
  let domainStart = getDomainStart(scales);
  let domainEnd;
  while (domainEnd = getNextStop(domainStart, scales)) {
    let sameTime = getMaxAtSameTime(domainStart, scales);
    if (sameTime) output.push(sameTime);
    let candidates = getScalesCovering([domainStart, domainEnd], scales);
    let pixelsPerMinute = _.max(candidates.map(d => d.pixelsPerMinute));
    if (pixelsPerMinute === undefined) {
      pixelsPerMinute = defaultPixelsPerMinute;
    }
    output.push({
      domain: [domainStart, domainEnd],
      pixelsPerMinute
    });
    domainStart = domainEnd;
  }
  return output;
}

function compactScales(scales) {
  let compact = [];
  let i = 0;
  while (i < scales.length) {
    let begin = scales[i].domain[0];
    let pixelsPerMinute = scales[i].pixelsPerMinute;
    let numberOfEvents = 1;
    let end;
    let scale;
    while ((scale = scales[i]) && scale.pixelsPerMinute === pixelsPerMinute) {
      end = scale.domain[1];
      numberOfEvents += scale.numberOfEvents ? scale.numberOfEvents - 1 : 1;
      i++;
    }
    compact.push({
      domain: [begin, end],
      numberOfEvents,
      pixelsPerMinute
    });
  }
  return compact;
}

function scaleFromScales(minGap, scales) {

  let domain = [];
  let range = [];
  let exceptions = {};
  let y = 0;

  if (scales.length > 0) {

    domain.push(scales[0].domain[0]);
    range.push(0);

    scales.forEach(scale => {
      let domainStart = scale.domain[0];
      let domainEnd = scale.domain[1];
      let dy;
      if (scale.pixelsPerMinute === Infinity) {
        dy = minGap * (scale.numberOfEvents - 1);
        exceptions[+domainStart] = y;
      } else {
        let minutes = (domainEnd - domainStart) / (1000 * 60);
        dy = minutes * scale.pixelsPerMinute;
      }
      domain.push(domainEnd);
      range.push(y += dy);
    });
  }

  return {
    domain,
    range,
    exceptions
  };
}

function fixOverlapping(minGap, points) {
  let nested = d3.nest()
      .key(d => d.pos)
      .sortKeys(d3.ascending)
      .entries(points);
  let overlapping = nested.filter(d => d.values.length > 1)
      .map(d => d.values);
  overlapping.forEach(points => {
    for (let i = 1; i < points.length; i++) {
      points[i].pos += i * minGap;
    }
  });
  return points;
}

export default function(collections) {

  let minGap = 0,
      maxGap = Infinity,
      pixelsPerMinute = 1;

  let exceptions = {};

  let noOverlap = d3.time.scale();

  noOverlap.minGap = function(x) {
    if (!arguments.length) return minGap;
    minGap = x;
    return noOverlap;
  };

  noOverlap.maxGap = function(x) {
    if (!arguments.length) return maxGap;
    maxGap = x;
    return noOverlap;
  };

  noOverlap.pixelsPerMinute = function(x) {
    if (!arguments.length) return pixelsPerMinute;
    pixelsPerMinute = x;
    return noOverlap;
  };

  noOverlap.positions = function(events, accessor = (d) => d) {
    let points = events.map(event => {
      let time = accessor(event);
      event.pos = (+time in exceptions) ? exceptions[+time] : noOverlap(time);
      return event;
    });
    return fixOverlapping(minGap, points);
  };

  noOverlap.build = function(collections) {
    let pass = collections
      .map(events => events.sort())
      .map(events => calcScales(pixelsPerMinute, minGap, maxGap, events))
      .map(compactScales);
    let scales = compactScales(combineScales(pixelsPerMinute, pass));
    let { domain, range, exceptions:ex } = scaleFromScales(minGap, scales);
    if (domain.length > 1) noOverlap.domain(domain);
    if (range.length > 1) noOverlap.range(range);
    exceptions = ex;
    return noOverlap;
  };

  return noOverlap;
}

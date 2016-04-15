import _ from "lodash";
import noOverlap from "./no-overlap-time-scale";
import sameService from "./same-service";

export function getServiceKey(segment) {
  return _.pick(segment, ["headcode", "origin_location", "origin_departure"]);
}

export function getServicesFromSegments(segments) {
  return _(segments)
    .map(getServiceKey)
    .uniqWith(_.isEqual)
    .value();
}

export function getSegmentsMatchingService(segments, service) {
  return segments.filter(s => sameService(s, service));
}

export function getScaleFromSegments(segments) {

  let routes = _.flatten(segments.map(segment => {
    return [
      segment.trust,
      segment.gps
    ]
  }));

  let eventTimes = routes.map(stops => stops.map(stop => stop.event_time));

  let scale = noOverlap()
      .minGap(12)
      .maxGap(50)
      .pixelsPerMinute(6)
      .build(eventTimes);

  return scale;
}

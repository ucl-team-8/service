import _ from "lodash";
import noOverlap from "./no-overlap-time-scale";

export function getServiceStopsFromSegment(segment) {
  return _(segment.matching)
    .map(d => d.trust)
    .compact()
    .sortBy(d => d.event_time)
    .value();
}

export function getUnitStopsFromSegment(segment) {
  return _(segment.matching)
    .map(d => d.gps)
    .compact()
    .sortBy(d => d.event_time)
    .value();
}

export function getServiceFromSegment(segment) {
  return _.pick(segment, ["headcode", "origin_location", "origin_departure"]);
}

export function getServicesFromSegments(segments) {
  return _(segments)
    .map(getServiceFromSegment)
    .uniqWith(_.isEqual)
    .value();
}

export function getSegmentsMatchingService(segments, service) {
  return segments.filter(segment => {
    let s = getServiceFromSegment(segment);
    return _.isEqual(s, service);
  });
}

export function getScaleFromSegments(segments) {

  let routes = _.flatten(segments.map(segment => {
    return [
      getServiceStopsFromSegment(segment),
      getUnitStopsFromSegment(segment)
    ]
  }));

  let eventTimes = routes.map(stops => stops.map(stop => stop.event_time));

  let scale = noOverlap()
      .minGap(12)
      .maxGap(50)
      .pixelsPerMinute(5)
      .build(eventTimes);

  return scale;
}

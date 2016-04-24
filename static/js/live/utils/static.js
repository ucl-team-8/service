import _ from "lodash";
import { getServiceKey } from "./segments";

export function getMatchingsFromAugmented(augmented) {
  return augmented.map(d => {
    return {
      headcode: d.headcode,
      origin_location: d.origin_location,
      origin_departure: d.origin_departure,
      units: _(d.units)
        .groupBy("type")
        .mapValues(d => d.map(d => d.gps_car_id))
        .value()
    }
  })
}

export function getSegmentsFromSelected(selected) {
  if (selected == null) return [];
  let service = _.find(window.augmented, selected);
  let segments = [];
  if (service) {
    segments.push({
      headcode: service.headcode,
      origin_location: service.origin_location,
      origin_departure: service.origin_departure,
      type: "service"
    });
    segments = segments.concat(service.units);
  }
  segments.forEach(segment => attachReports(segment, window.services, window.units));
  return segments;
}

function attachReports(segment) {

  let serviceKey = getServiceKey(segment);
  let unitKey = { gps_car_id: segment.gps_car_id };

  if (segment.trust == null && serviceKey) {
    let service = _.find(window.services, serviceKey);
    let trust = service ? service.reports : [];
    if (segment.start && segment.end) {
      trust = trust.filter(d => d.event_time >= segment.start && d.event_time <= segment.end);
    }
    segment.trust = _.sortBy(trust, "event_time");
  }

  if (segment.gps == null && unitKey) {
    let unit = _.find(window.units, unitKey);
    let gps = unit ? unit.reports : [];
    if (segment.start && segment.end) {
      gps = gps.filter(d => d.event_time >= segment.start && d.event_time <= segment.end);
    }
    segment.gps = _.sortBy(gps, "event_time");
  }
}

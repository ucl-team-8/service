import _ from "lodash";

export default function sameService(a, b) {
  if (a == null || b == null) return false;
  return a.headcode === b.headcode &&
         a.origin_location === b.origin_location &&
         _.isEqual(a.origin_departure, b.origin_departure);
}

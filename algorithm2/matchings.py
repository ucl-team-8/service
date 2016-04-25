import env
from db_queries import get_service_matchings_for_unit
from utils import get_interval_overlap, time_intervals_overlap, flip_matchings, date_to_iso, get_service_key
from collections import defaultdict
from datetime import timedelta

class Matchings:

    def __init__(self, allocations, tracker):
        self.allocations = allocations
        self.tracker = tracker
        self.unit_matchings = dict()

    def is_likely_match(self, service_matching_props):

        s = service_matching_props
        service = get_service_key(s)
        unit = s['gps_car_id']

        if self.allocations.was_planned(service, unit):
            return True

        interval = s['end'] - s['start']
        corrected_error = env.get_corrected_error(s['mean_time_error'])
        matched_over_total = float(s['total_matching']) / self.tracker.get_total_for_service(service)

        low_error_if_few_reports = s['total_matching'] > 5 or (s['variance_time_error'] < 2.0 and abs(corrected_error) < 1.0)
        insignificant = matched_over_total < 0.35 and interval < timedelta(minutes=15)

        return s['total_matching'] > 2 and \
               s['variance_time_error'] < 6.0 and \
               abs(corrected_error) < 1.5 and \
               low_error_if_few_reports and \
               not insignificant

    def get_match_score(self, service_matching_props):

        s = service_matching_props
        service = get_service_key(service_matching_props)
        unit = s['gps_car_id']
        corrected_error = env.get_corrected_error(s['mean_time_error'])

        was_planned = self.allocations.was_planned(service, unit)

        close_match = s['total_matching'] > 8 and \
                      abs(corrected_error) < 1.0 and \
                      s['variance_time_error'] < 2.0

        # intentionally coerces to int to form buckets
        total_matching_score = int(s['total_matching'] / 5)

        error_score = int(abs(corrected_error) / 0.4)

        matched_over_total = float(s['total_matching']) / self.tracker.get_total_for_service(service)
        matched_over_total_score = int(matched_over_total / 0.25) # 4 buckets essentially

        meets_low = s['variance_time_error'] < 3.0 or \
                   (s['variance_time_error'] < 5.0 and s['total_matching'] < 6)

        return (
            -int(was_planned),              # descending
            -int(close_match),              # descending
            -int(total_matching_score),     # descending
            int(error_score),               # ascending
            -int(matched_over_total_score), # descending
            -int(meets_low)                 # descending
        )

    def update_matchings_for(self, changed_keys):

        changed_units = set(k[3] for k in changed_keys)

        for unit in changed_units:

            service_matchings = get_service_matchings_for_unit(unit)
            service_matchings = [s.as_dict() for s in service_matchings]
            service_matchings = filter(lambda s: self.is_likely_match(s), service_matchings)
            service_matchings = sorted(service_matchings, key=self.get_match_score)

            true_matches = list()

            for s in service_matchings:

                # detects of any existing matches overlap for more than `env.max_overlap`
                overlaps_with_existing = any(
                    self.overlaps_significantly(s,x) for x in true_matches)

                if not overlaps_with_existing:
                    true_matches.append(s)

            self.unit_matchings[unit] = map(get_service_key, true_matches)

    def get_all_matchings(self):
        """The final pass of the matching algorithm that decides which service
        was ran by each unit.
        """
        return flip_matchings(self.unit_matchings)

    def overlaps_significantly(self, s1, s2):
        overlap = get_interval_overlap(s1['start'], s1['end'], s2['start'], s2['end'])
        one_is_inside_the_other = s1['start'] <= s2['start'] == s1['end'] >= s2['end']
        return overlap > env.max_overlap or one_is_inside_the_other

    def get_matchings_diff(self, proposed):
        """Gets a dictionary of proposed allocations (output of `get_matchings`)
        and returns the:

        - unplanned allocations that the algorithm allocated but are not in the
          genius allocations
        - mismatched allocations that the algorithm didn't allocate but *are* in
          the genius allocations

        """
        matchings = dict()

        for service in self.tracker.get_all_services():

            # insert service in matchings
            matchings[service] = dict()

            # get proposed units (from algorithm) and allocated (from allocations)
            proposed_units = proposed[service] if service in proposed else set()
            allocated_units = self.allocations.get_units_for_service(service)

            # unchanged are those that we think are good matchings and are also in
            # the allocations
            unchanged_units = proposed_units.intersection(allocated_units)

            # added are those that we think are good matchings, but are not
            # in the (genius) allocations
            added_units = proposed_units - allocated_units

            # removed are those that are in the (genius) allocations, but
            # the algorithm doesn't think they're good matchings
            removed_units = allocated_units - proposed_units

            # no_data_units are the units we don't have enough data about
            no_data_units = set()
            service_time_range = self.tracker.get_service_time_range(service)
            # check to see if we the first and last report we received from the
            # unit are within the time the service was running
            for unit in removed_units:
                unit_time_range = self.tracker.get_unit_time_range(unit)
                # if there is no time range, we never received an event from unit
                if not unit_time_range:
                    no_data_units.add(unit)
                    continue
                # TODO but not really: to make this more accurate, we need to
                # check in the database whether a gps event occurred during the
                # time the service was running
                overlap = time_intervals_overlap(service_time_range['start'],
                                              service_time_range['end'],
                                              unit_time_range['start'],
                                              unit_time_range['end'])
                if not overlap:
                    no_data_units.add(unit)

            # discard no_data_units
            removed_units -= no_data_units

            if unchanged_units: # if not empty
                matchings[service]['unchanged'] = unchanged_units
            if added_units:
                matchings[service]['added'] = added_units
            if removed_units:
                matchings[service]['removed'] = removed_units
            if no_data_units:
                matchings[service]['no_data'] = no_data_units


        return matchings

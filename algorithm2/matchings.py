import env
from db_queries import get_service_matchings_for_unit
from utils import get_interval_overlap, time_intervals_overlap, flip_matchings, date_to_iso
from collections import defaultdict

class Matchings:

    def __init__(self, allocations, tracker):
        self.allocations = allocations
        self.tracker = tracker

    def get_corrected_error(self, error):
        return error - env.trust_delay

    # TODO: just use `not is_likely_match` here?
    def is_unlikely_match(self, service_matching_props):
        return False
        """Given a dictionary (representing a ServiceMatching row) it returns
        whether it's a *remotely* likely a match.

        Used by the service_matcher to decide whether it's worth storing it in
        the database.

        """
        s = service_matching_props
        corrected_error = self.get_corrected_error(s['median_time_error'])
        return s['total_matching'] < 2 or \
               abs(corrected_error) > 1.5

    def is_likely_match(self, service_matching_props):
        s = service_matching_props
        corrected_error = self.get_corrected_error(s['median_time_error'])
        missed_over_total = s['total_missed_in_between'] / s['total_matching']
        if s['total_matching'] <= 2:
            return False
        elif s['total_matching'] <= 5:
            return True if abs(corrected_error) < 0.75 and s['iqr_time_error'] < 2.0 and missed_over_total < 0.8 else False
        elif abs(corrected_error) < 0.75 and s['iqr_time_error'] < 2.5 and missed_over_total < 0.6:
            return True
        else:
            return False

    def get_all_matchings(self):
        """The final pass of the matching algorithm that decides which service
        was ran by each unit.
        """
        unit_matchings = dict()

        for unit in self.tracker.get_all_units():

            service_matchings = list(get_service_matchings_for_unit(unit))
            service_matchings = filter(lambda s: self.is_likely_match(s.as_dict()), service_matchings)
            service_matchings = sorted(service_matchings,
                                       key=lambda s: s.total_matching, reverse=True)

            true_matches = set()

            for s in service_matchings:

                # detects of any existing matches overlap for more than `env.max_overlap`
                overlaps_with_existing = any(
                    self.overlaps_significantly(s,x) for x in true_matches)

                if not overlaps_with_existing:
                    true_matches.add(s)

            unit_matchings[unit] = set((s.headcode, s.origin_location, s.origin_departure) for s in true_matches)

        service_matchings = flip_matchings(unit_matchings)

        return service_matchings

    def overlaps_significantly(self, s1, s2):
        overlap = self.service_matchings_overlap(s1, s2)
        return overlap > env.max_overlap or \
               (s1.start <= s2.start == s1.end >= s2.end)

    def service_matchings_overlap(self, s1, s2):
        return get_interval_overlap(s1.start, s1.end, s2.start, s2.end)

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

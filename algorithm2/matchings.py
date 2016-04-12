import env
from db_queries import get_service_matchings_for_unit
from utils import time_intervals_overlap, convert_matchings
from collections import defaultdict

class Matchings:

    def __init__(self, allocations, tracker):
        self.allocations = allocations
        self.tracker = tracker

    def get_corrected_error(self, error):
        return error - env.trust_delay

    def is_unlikely_match(self, service_matching_props):
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
        if s['total_matching'] <= 2:
            return False
        elif s['total_matching'] <= 3:
            return True if abs(corrected_error) < 0.75 and s['iqr_time_error'] < 2.5 else False
        elif abs(corrected_error) < 1.0 and s['iqr_time_error'] < 3.0:
            return True
        else:
            return False

    def get_matchings(self):
        """The final pass of the matching algorithm that decides which service
        was ran by each unit.
        """
        unit_matchings = dict()

        for unit in self.tracker.get_all_units():

            service_matchings = list(get_service_matchings_for_unit(unit))
            service_matchings = filter(lambda s: self.is_likely_match(s.as_dict()), service_matchings)
            service_matchings = sorted(service_matchings,
                                       key=lambda s: abs(self.get_corrected_error(s.median_time_error)))

            true_matches = set()

            for s in service_matchings:

                overlaps_with_existing = any(
                    self.service_matchings_overlap(s,x) for x in true_matches)

                if s.total_matching > 3 and not overlaps_with_existing:
                    true_matches.add(s)

            unit_matchings[unit] = set((s.headcode, s.origin_location, s.origin_departure) for s in true_matches)

        return convert_matchings(unit_matchings)


    def service_matchings_overlap(self, s1, s2):
        return time_intervals_overlap(s1.start, s1.end, s2.start, s2.end)

    def get_matchings_diff(self, proposed):
        """Gets a dictionary of proposed allocations (output of `get_matchings`)
        and returns the:

        - unplanned allocations that the algorithm allocated but are not in the
          genius allocations
        - mismatched allocations that the algorithm didn't allocate but *are* in
          the genius allocations

        """
        acc = defaultdict(dict)

        for service in self.tracker.get_all_services():
            proposed_units = proposed[service] if service in proposed else set()
            allocated_units = self.allocations.get_units_for_service(service)

            # unplanned are those that we think are good matchings, but are not
            # in the (genius) allocations
            unplanned_units = proposed_units - allocated_units

            # mismatching are those that are in the (genius) allocations, but
            # the algorithm didn't allocate them
            mismatching_units = allocated_units - proposed_units
            mismatching_units = [unit for unit in mismatching_units if self.tracker.get_total_for_unit(unit) > 10]
            # TODO: check if gps_car_id is "busy" during the time the allocated
            # service was running, if it isn't then likely we didn't have enough
            # data to detect it was running it

            if unplanned_units: # if not empty
                acc[service]['unplanned'] = unplanned_units
            if mismatching_units:
                acc[service]['mismatched'] = mismatching_units

        return dict(acc)

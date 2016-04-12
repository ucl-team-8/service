import env
from collections import defaultdict

class Matchings:

    def __init__(self, allocations):
        self.allocations = allocations
        self.services = dict()
        self.units = dict()

    def seen_service(self, service):
        if service not in self.services:
            self.services[service] = 1
        else:
            self.services[service] += 1

    def seen_unit(self, unit):
        if unit not in self.units:
            self.units[unit] = 1
        else:
            self.units[unit] += 1

    def get_total_for_service(self, service):
        if service in self.services:
            return self.services[service]
        else:
            return 0

    def get_total_for_unit(self, unit):
        if unit in self.units:
            return self.units[unit]
        else:
            return 0

    def get_all_services(self):
        return self.services.keys()

    def get_all_units(self):
        return self.units.keys()

    def unlikely_match(self, service_matching_props):
        """Given a dictionary (representing a ServiceMatching row) it returns
        whether it's a remotely likely match.

        Used by the service_matcher to decide whether it's worth storing it in
        the database.

        """
        s = service_matching_props
        service = (s['headcode'], s['origin_location'], s['origin_departure'])
        corrected_error = s['median_time_error'] - env.trust_delay
        return s['total_matching'] < 2 or \
               abs(corrected_error) > 3.0

    # TODO: the two methods below should be refactored into one.

    def get_matchings(self):


    def get_matchings_diff(self, proposed):
        """Gets a dictionary of proposed allocations and returns the ones that
        were proposed but not planned in allocations.
        """
        acc = defaultdict(dict)
        for service, proposed_units in proposed.iteritems():
            allocated_units = self.allocations.get_units_for_service(service)

            # unplanned are those that we think are good matchings, but are not
            # in the (genius) allocations
            unplanned_units = proposed_units - allocated_units

            # mismatching are those
            mismatching_units = allocated_units - proposed_units
            mismatching_units = [unit for unit in mismatching_units if self.get_total_for_unit(unit) > 4]

            if unplanned_units: # if not empty
                acc[service]['unplanned'] = unplanned_units
            if mismatching_units:
                acc[service]['mismatched'] = mismatching_units

        return acc

    # def get_mismatching(self, proposed_mismatching):
    #     """Gets a dictionary of allocations containing units that didn't match
    #     the service (according to the algorithm) and out of those, it returns
    #     the ones that were planned (in allocations).
    #     """
    #     mismatching = dict()
    #     for service, proposed_mismatching_units in proposed_mismatching.iteritems():
    #         allocated_units = self.allocations.get_units_for_service(service)
    #         mismatching_units = proposed_mismatching_units.intersection(allocated_units)
    #         if mismatching_units: # if not empty
    #             mismatching[service] = mismatching_units
    #     return mismatching


class Matchings:

    def __init__(self, allocations):
        self.allocations = allocations
        self.services = set()
        self.units = set()

    def seen_service(self, service):
        self.services.add(service)

    def seen_unit(self, unit):
        self.units.add(unit)

    def get_matchings(self):
        pass

    # TODO: the two methods below should be refactored into one.

    def get_unplanned(self, proposed):
        """Gets a dictionary of proposed allocations and returns the ones that
        were proposed but not planned in allocations.
        """
        unplanned = dict()
        for service, proposed_units in proposed.iteritems():
            allocated_units = self.allocations.get_units_for_service(service)
            unplanned_units = proposed_units - allocated_units
            if unplanned_units: # if not empty
                unplanned[service] = unplanned_units
        return unplanned

    def get_mismatching(self, proposed_mismatching):
        """Gets a dictionary of allocations containing units that didn't match
        the service (according to the algorithm) and out of those, it returns
        the ones that were planned (in allocations).
        """
        mismatching = dict()
        for service, proposed_mismatching_units in proposed_mismatching.iteritems():
            allocated_units = self.allocations.get_units_for_service(service)
            mismatching_units = proposed_mismatching_units.intersection(allocated_units)
            if mismatching_units: # if not empty
                mismatching[service] = mismatching_units
        return mismatching

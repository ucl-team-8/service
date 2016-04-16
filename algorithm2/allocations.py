import copy
from models import Schedule
from db_queries import db_session

class Allocations:
    """Stores the genius allocations (and provides useful functions for them).
    """

    def __init__(self):
        self.service_allocations, self.unit_allocations = self.__get_allocations()

    def get_units_for_service(self, service):
        """Returns a set of the units allocated to a service. It expects the
        service as a tuple of (headcode, origin_location, origin_departure)
        """
        if service not in self.service_allocations:
            return set()
        else:
            return copy.deepcopy(self.service_allocations[service])

    def get_services_for_unit(self, unit):
        """Returns a set of services allocated to a unit. It expects a string of
        the gps_car_id.
        """
        if unit not in self.unit_allocations:
            return set()
        else:
            return copy.deepcopy(self.unit_allocations[unit])

    def was_planned(self, service, unit):
        if service not in self.service_allocations:
            return False
        else:
            return unit in self.service_allocations[service]

    def __get_allocations(self):
        """Retrieves the allocations from the database.
        """

        query = db_session.query(Schedule).all()

        db_session.close()

        service_allocations = dict()
        unit_allocations = dict()

        for alloc in query:

            service = (alloc.headcode, alloc.origin_location, alloc.origin_departure)
            unit = alloc.unit

            if service not in service_allocations:
                service_allocations[service] = set()
            service_allocations[service].add(unit)

            if unit not in unit_allocations:
                unit_allocations[unit] = set()
            unit_allocations[unit].add(service)

        return (service_allocations, unit_allocations)

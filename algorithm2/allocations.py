import copy
from app_db import db
from models import Schedule

class Allocations:

    def __init__(self):
        self.allocations = self.__get_allocations()

    def get_allocations(self):
        return copy.deepcopy(self.allocations)

    def get_units_for_service(self, service):
        if service not in self.allocations:
            return set()
        else:
            return copy.deepcopy(self.allocations[service])

    def __get_allocations(self):

        query = db.session.query(Schedule).all()
        allocations = dict()

        for alloc in query:
            service = (alloc.headcode, alloc.origin_location, alloc.origin_departure)
            unit = alloc.unit
            if service not in allocations:
                allocations[service] = set()
            allocations[service].add(unit)

        return allocations

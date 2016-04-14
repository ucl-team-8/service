import env
from collections import defaultdict

default_dict = lambda: { 'total_stops': 0, 'first_seen': None, 'last_seen': None }

class Tracker:
    """Tracks which services/units have been "seen" from the event stream.
    """

    def __init__(self):
        # dictionary with service/unit as key and number of reports as value
        # essentially stores number of events per service/unit
        # the service key is a tuple of (headcode, origin_location, origin_departure)
        self.services = defaultdict(default_dict)
        self.units = defaultdict(default_dict)

    def seen_service(self, service):
        if service not in self.services:
            self.services[service]['first_seen'] = env.now
        self.services[service]['last_seen'] = env.now
        self.services[service]['total_stops'] += 1

    def seen_unit(self, unit):
        if unit not in self.units:
            self.units[unit]['first_seen'] = env.now
        self.units[unit]['last_seen'] = env.now
        self.units[unit]['total_stops'] += 1

    def get_total_for_service(self, service):
        if service in self.services:
            return self.services[service]['total_stops']
        else:
            return 0

    def get_total_for_unit(self, unit):
        if unit in self.units:
            return self.units[unit]['total_stops']
        else:
            return 0

    def get_all_services(self):
        return set(self.services.keys())

    def get_all_units(self):
        return set(self.units.keys())

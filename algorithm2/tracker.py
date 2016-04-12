class Tracker:
    """Tracks which services/units have been "seen" from the event stream.
    """

    def __init__(self):
        # dictionary with service/unit as key and number of reports as value
        # essentially stores number of events per service/unit
        # the service key is a tuple of (headcode, origin_location, origin_departure)
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
        return set(self.services.keys())

    def get_all_units(self):
        return set(self.units.keys())

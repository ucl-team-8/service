
class MatcherQueue:
    """Temporarily stores event matchings (trust->gps) passed from the Consumer.

    The event matchings are stored as dictionaries, with the fields of
    EventMatching table as keys, ready to be inserted into the database.

    Also stores the primary keys of the service matchings (service->unit, see
    ServiceMatching) that need to be updated. The updating is done by the
    Matcher.

    """

    def __init__(self):
        self.new_rows = []
        self.changed_matchings = set()

    def add(self, trust, gps):

        row = self.__get_matching_props(trust, gps)
        self.new_rows.append(row)

        service = (trust.headcode,
                   trust.origin_location,
                   trust.origin_departure)
        unit = gps.gps_car_id
        self.changed_matchings.add((service, unit))

    def pop_new_rows(self):
        new_rows = self.new_rows
        self.new_rows = []
        return new_rows

    def pop_changed_matchings(self):
        changed_matchings = self.changed_matchings
        self.changed_matchings = set()
        return changed_matchings

    def __get_matching_props(self, trust, gps):
        return {
            'headcode': trust.headcode,
            'origin_location': trust.origin_location,
            'origin_departure': trust.origin_departure,
            'gps_car_id': gps.gps_car_id,
            'trust_id': trust.id,
            'gps_id': gps.id,
            'trust_event_time': trust.event_time,
            'gps_event_time': gps.event_time
        }

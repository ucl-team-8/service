
class MatcherQueue:
    """Temporarily stores event matchings (trust->gps) passed from the EventMatcher.

    The event matchings are stored as dictionaries, with the fields of
    EventMatching table as keys, ready to be inserted into the database.

    Also stores the primary keys of the service matchings (service->unit, see
    ServiceMatching) that need to be updated. The updating is done by the
    ServiceMatcher.

    """

    def __init__(self):
        self.event_matching_rows = []
        self.changed_service_matchings = set()

    def add(self, trust, gps):

        row = self.__get_matching_props(trust, gps)
        self.event_matching_rows.append(row)

        service = (trust.headcode,
                   trust.origin_location,
                   trust.origin_departure)
        unit = gps.gps_car_id
        self.changed_service_matchings.add(service + (unit,))

    def pop_event_matching_rows(self):
        event_matching_rows = self.event_matching_rows
        self.event_matching_rows = []
        return event_matching_rows

    def pop_changed_service_matchings_keys(self):
        changed_service_matchings = self.changed_service_matchings
        self.changed_service_matchings = set()
        return changed_service_matchings

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

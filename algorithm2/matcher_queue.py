
class MatcherQueue:

    def __init__(self):
        self.rows = []
        self.changed_matchings = set()

    def add(self, trust, gps):

        row = self.__get_matching_props(trust, gps)
        self.rows.append(row)

        service = (trust.headcode,
                   trust.origin_location,
                   trust.origin_departure)
        unit = gps.gps_car_id
        self.changed_matchings.add((service, unit))

    def pop_rows(self):
        rows = self.rows
        self.rows = []
        return rows

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

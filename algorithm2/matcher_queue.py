from collections import defaultdict
from utils import get_service_key, flatten

class MatcherQueue:
    """Temporarily stores event matchings (trust->gps) passed from the EventMatcher.

    The event matchings are stored as dictionaries, with the fields of
    EventMatching table as keys, ready to be inserted into the database.

    Also stores the primary keys of the service matchings (service->unit, see
    ServiceMatching) that need to be updated. The updating is done by the
    ServiceMatcher.

    """

    def __init__(self):
        self.event_matchings = defaultdict(list)

    def add(self, trust, gps):
        service = get_service_key(trust)
        unit = gps['gps_car_id']
        key = service + (unit,)
        event_matching = self.__get_event_matching_props(trust, gps)
        self.event_matchings[key].append(event_matching)

    def pop_event_matchings(self):
        event_matchings = flatten(self.event_matchings.values())
        # self.event_matchings = defaultdict(list)
        return event_matchings

    def pop_changed_service_matchings_keys(self):
        changed_service_matchings = set(self.event_matchings.keys())
        self.event_matchings = defaultdict(list)
        return changed_service_matchings

    def __get_event_matching_props(self, trust, gps):
        return {
            'headcode': trust['headcode'],
            'origin_location': trust['origin_location'],
            'origin_departure': trust['origin_departure'],
            'gps_car_id': gps['gps_car_id'],
            'trust_id': trust['id'],
            'gps_id': gps['id'],
            'trust_event_time': trust['event_time'],
            'gps_event_time': gps['event_time']
        }

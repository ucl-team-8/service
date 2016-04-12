import env
from db_queries import db_session, get_event_matchings, get_service_matching
from models import EventMatching, ServiceMatching
from utils import diff_seconds, median, iqr

class ServiceMatcher:
    """This class does 2 things:

    1. Inserts event matchings from the queue to the database.
    2. Takes the primary keys of the service matchings (from the queue) that
       need to be updated, updates them and stores them in the database.

    """

    def __init__(self, queue, matchings):
        self.queue = queue
        self.matchings = matchings

    def run(self):
        self.save_event_matchings()
        self.save_service_matchings()

    def save_event_matchings(self):
        """Takes all queued rows from the MatcherQueue and adds them to the
        database.
        """
        db_session.bulk_insert_mappings(EventMatching, self.queue.pop_event_matching_rows())
        db_session.commit()

    def save_service_matchings(self):
        """Takes the primary keys of the service matchings (from the queue) that
           need to be updated, updates them and stores them in the database.
        """

        changed_matchings = self.queue.pop_changed_service_matchings()

        insert, update = [], []

        # TODO: can be more efficient if it gets existing primary keys with a
        # single query, rather than querying for each one.

        for service, unit in changed_matchings:
            service_matching = self.get_service_matching_props(service, unit)
            # ignore service matching if unlikely matching
            if self.matchings.is_unlikely_match(service_matching):
                continue
            # otherwise add it to update or insert list
            if get_service_matching(service, unit):
                update.append(service_matching)
            else:
                insert.append(service_matching)

        db_session.bulk_insert_mappings(ServiceMatching, insert)
        db_session.bulk_update_mappings(ServiceMatching, update)

        db_session.commit()

        # TODO: socketio notify each changed

    def get_service_matching_props(self, service, unit):
        """Returns an instance of ServiceMatching (a table row essentially) with
        all the fields calculated and populated.
        """

        headcode, origin_location, origin_departure = service
        gps_car_id = unit

        event_matchings = get_event_matchings(service, unit)

        # getting the start and the end
        trust_times = [m.trust_event_time for m in event_matchings]
        gps_times = [m.gps_event_time for m in event_matchings]
        all_times = trust_times + gps_times
        start = min(all_times)
        end = max(all_times)

        time_errors = [diff_seconds(a, b) / 60.0 for a, b in zip(trust_times, gps_times)]

        # we only want the unique trust events (they can repeat in matchings)
        total_matching = len(set(m.trust_id for m in event_matchings))
        total_for_service = self.matchings.get_total_for_service(service)

        return {
            'headcode': headcode,
            'origin_location': origin_location,
            'origin_departure': origin_departure,
            'gps_car_id': gps_car_id,
            'median_time_error': median(time_errors),
            'iqr_time_error': iqr(time_errors),
            'total_matching': total_matching,
            'matched_over_total': float(total_matching) / total_for_service,
            'start': start,
            'end': end
        }

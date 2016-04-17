import env
from db_queries import db_session, get_service_matchings_by_keys
from models import ServiceMatching
from utils import diff_minutes, average, variance, pkey_from_service_matching, pkey_from_service_matching_props, combine_stats

class ServiceMatcher:
    """Pprocesses event matchings from the queue and creates/updates service
    matchings in the database.

    """

    def __init__(self, queue):
        self.queue = queue

    def run(self):
        self.save_matchings()

    def save_matchings(self):
        """Takes the primary keys of the service matchings (from the queue) that
           need to be updated, updates them and stores them in the database.
        """

        new_matchings = self.queue.pop_event_matchings()

        # changed_keys = self.queue.pop_changed_service_matchings_keys()
        changed_keys = set(new_matchings.keys())

        existing_matchings = get_service_matchings_by_keys(changed_keys)
        existing_keys = set(map(pkey_from_service_matching, existing_matchings))
        new_keys = changed_keys - existing_keys

        insert, update = [], []

        for old_matching in existing_matchings:
            old_matching = old_matching.as_dict()
            pkey = pkey_from_service_matching_props(old_matching)
            event_matchings = new_matchings[pkey]
            new_matching = self.generate_from_event_matchings(pkey, event_matchings)
            combined_matching = self.combine_matchings(old_matching, new_matching)
            update.append(combined_matching)

        for pkey in new_keys:
            event_matchings = new_matchings[pkey]
            new_matching = self.generate_from_event_matchings(pkey, event_matchings)
            insert.append(new_matching)

        # insert
        db_session.bulk_insert_mappings(ServiceMatching, insert)

        # update
        db_session.bulk_update_mappings(ServiceMatching, update)

        db_session.commit()
        db_session.close()

    def generate_from_event_matchings(self, pkey, event_matchings):

        event_matchings = self.filter_closest_matchings(event_matchings)

        headcode, origin_location, origin_departure, gps_car_id = pkey

        trust_times = [m['trust_event_time'] for m in event_matchings]
        gps_times = [m['gps_event_time'] for m in event_matchings]
        all_times = trust_times + gps_times
        start = min(all_times)
        end = max(all_times)

        time_errors = [diff_minutes(a, b) for a, b in zip(trust_times, gps_times)]

        return {
            'headcode': headcode,
            'origin_location': origin_location,
            'origin_departure': origin_departure,
            'gps_car_id': gps_car_id,
            'mean_time_error': average(time_errors),
            'variance_time_error': variance(time_errors),
            'total_matching': len(event_matchings),
            'start': start,
            'end': end
        }

    def combine_matchings(self, old, new):

        combined = new.copy()

        old_stats = (old['total_matching'], old['mean_time_error'], old['variance_time_error'])
        new_stats = (new['total_matching'], new['mean_time_error'], new['variance_time_error'])

        total, mean, variance = combine_stats(old_stats, new_stats)

        combined['mean_time_error'] = mean
        combined['variance_time_error'] = variance
        combined['total_matching'] = total
        combined['start'] = min(old['start'], new['start'])
        combined['end'] = max(old['end'], new['end'])

        return combined

    def filter_closest_matchings(self, event_matchings):

        filtered = []

        def sorting_key(m):
            error = diff_minutes(m['trust_event_time'], m['gps_event_time'])
            return abs(env.get_corrected_error(error))

        event_matchings = sorted(event_matchings, key=sorting_key)

        seen_trust = set()
        seen_gps = set()

        for m in event_matchings:
            if m['trust_id'] not in seen_trust and m['gps_id'] not in seen_gps:
                filtered.append(m)
            seen_trust.add(m['trust_id'])
            seen_gps.add(m['gps_id'])

        return filtered

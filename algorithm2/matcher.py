from app_db import db
import env
from models import EventMatching, ServiceMatching
from utils import diff_seconds, median, variance

class Matcher:

    def __init__(self, queue):
        self.queue = queue
        self.last_run = env.now

    def run(self):
        self.save_event_matchings()
        self.save_service_matchings()
        self.last_run = env.now

    def save_event_matchings(self):
        db.session.bulk_insert_mappings(EventMatching, self.queue.pop_rows())
        db.session.commit()

    def save_service_matchings(self):
        changed_matchings = self.queue.pop_changed_matchings()
        for service, unit in changed_matchings:
            headcode, origin_location, origin_departure = service
            gps_car_id = unit
            service_matching = self.get_service_matching(
                headcode,
                origin_location,
                origin_departure,
                gps_car_id)
            db.session.merge(service_matching)
        db.session.commit()
        # TODO: socketio notify each changed
        self.changed = set()

    def get_service_matching(self, headcode, origin_location, origin_departure, gps_car_id):

        event_matchings = db.session.query(EventMatching).filter_by(
            headcode=headcode,
            origin_location=origin_location,
            origin_departure=origin_departure,
            gps_car_id=gps_car_id)

        trust_times = [m.trust_event_time for m in event_matchings]
        gps_times = [m.gps_event_time for m in event_matchings]

        all_times = trust_times + gps_times
        start = min(all_times)
        end = max(all_times)

        time_errors = [diff_seconds(a, b) / 60.0 for a, b in zip(trust_times, gps_times)]

        service_matching = ServiceMatching(
            headcode=headcode,
            origin_location=origin_location,
            origin_departure=origin_departure,
            gps_car_id=gps_car_id,
            total_matching=len(time_errors),
            median_time_error=median(time_errors),
            variance_time_error=variance(time_errors),
            start=start,
            end=end
        )

        return service_matching

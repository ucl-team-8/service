from app_db import db
import env
from models import EventMatching, ServiceMatching
from datetime import timedelta
from utils import diff_seconds, median, variance

class Matcher:

    def __init__(self):
        self.last_run = env.now
        self.run_delay = timedelta(minutes=env.run_delay)
        self.new_rows = []
        self.changed = set()

    def add(self, trust, gps):

        row = self.__get_matching_props(trust, gps)
        self.new_rows.append(row)

        service = (trust.headcode,
                   trust.origin_location,
                   trust.origin_departure)
        unit = gps.gps_car_id
        self.changed.add((service, unit))

        self.run_if_ready()

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

    def run_if_ready(self):
        if env.now - self.last_run > self.run_delay:
            self.run()

    def run(self):
        self.save_matchings()
        self.run_algorithm()
        self.last_run = env.now

    def save_matchings(self):
        db.session.bulk_insert_mappings(EventMatching, self.new_rows)
        db.session.commit()
        self.new_rows = []

    def run_algorithm(self):
        for service, unit in self.changed:
            headcode, origin_location, origin_departure = service
            gps_car_id = unit
            service_matching = self.get_service_matching(
                headcode,
                origin_location,
                origin_departure,
                gps_car_id)
            db.session.merge(service_matching)
        db.session.commit()
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

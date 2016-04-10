from app_db import db
import env
from models import EventMatching
from datetime import timedelta
from utils import diff_seconds

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
        time_error = diff_seconds(trust.event_time, gps.event_time) / 60
        return {
            'headcode': trust.headcode,
            'origin_location': trust.origin_location,
            'origin_departure': trust.origin_departure,
            'gps_car_id': gps.gps_car_id,
            'trust_id': trust.id,
            'gps_id': gps.id,
            'time_error': time_error
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
        self.changed = set()

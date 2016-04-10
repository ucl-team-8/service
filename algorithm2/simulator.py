import env
from app_db import db
from windowed_query import windowed_query
from models import Trust, GPS

class Simulator:

    def __init__(self, consumer):
        self.consumer = consumer
        self.windowed_gps = windowed_query(db.session.query(GPS), GPS.event_time, 1000)
        self.windowed_trust = windowed_query(db.session.query(Trust), Trust.event_time, 1000)

    def get_next_gps(self):
        report = None
        try:
            report = self.windowed_gps.next()
        except StopIteration:
            pass
        return report

    def get_next_trust(self):
        report = None
        try:
            report = self.windowed_trust.next()
        except StopIteration:
            pass
        return report

    def set_now(self, date):
        env.now = date

    def simulate(self):

        next_gps = self.get_next_gps()
        next_trust = self.get_next_trust()

        while next_gps is not None or \
              next_trust is not None:

            if next_gps is not None and ((next_trust is None) or \
                next_gps.event_time < next_trust.event_time):

                self.consumer.consume_gps(next_gps)
                self.set_now(next_gps.event_time)
                next_gps = self.get_next_gps()

            else:
                self.consumer.consume_trust(next_trust)
                self.set_now(next_trust.event_time)
                next_trust = self.get_next_trust()

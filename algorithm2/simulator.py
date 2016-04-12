import env
import threading
from db_queries import db_session
from windowed_query import windowed_query
from models import Trust, GPS, EventMatching, ServiceMatching
from datetime import timedelta

class Simulator(threading.Thread):

    last_run = None

    def __init__(self):
        threading.Thread.__init__(self)

        from allocations import Allocations
        from matcher_queue import MatcherQueue
        from event_matcher import EventMatcher
        from socket_manager import SocketManager
        from matchings import Matchings
        from service_matcher import ServiceMatcher

        queue = MatcherQueue()
        allocations = Allocations()
        # socket_manager = SocketManager(socketio)
        matchings = Matchings(allocations=allocations)
        event_matcher = EventMatcher(queue=queue,
                                     matchings=matchings)
        service_matcher = ServiceMatcher(queue=queue,
                                         matchings=matchings)

        self.event_matcher = event_matcher
        self.service_matcher = service_matcher
        self.interval = timedelta(minutes=env.matcher_interval)
        self.windowed_gps = windowed_query(db_session.query(GPS), GPS.event_time, 1000)
        self.windowed_trust = windowed_query(db_session.query(Trust), Trust.event_time, 1000)

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
        if self.last_run is None:
            self.last_run = env.now
        # "simulating" running the service matcher at intervals
        # in production this would be some kind of scheduled task
        if env.now - self.last_run > self.interval:
            self.service_matcher.run()
            self.last_run = env.now

    def simulate(self):

        next_gps = self.get_next_gps()
        next_trust = self.get_next_trust()

        while next_gps is not None or \
              next_trust is not None:

            if next_gps is not None and ((next_trust is None) or \
                next_gps.event_time < next_trust.event_time):

                self.event_matcher.match_gps(next_gps)
                self.set_now(next_gps.event_time)
                next_gps = self.get_next_gps()

            else:
                self.event_matcher.match_trust(next_trust)
                self.set_now(next_trust.event_time)
                next_trust = self.get_next_trust()

        # run the matcher at the very end
        self.service_matcher.run()
        print("Finished matching.")

    def clear_tables(self):
        db_session.query(EventMatching).delete()
        db_session.query(ServiceMatching).delete()
        db_session.commit()

    def run(self):
        self.clear_tables()
        self.simulate()

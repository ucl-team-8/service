import env
import threading
from db_queries import db_session
from windowed_query import windowed_query
from models import Trust, GPS, EventMatching, ServiceMatching
from datetime import datetime, timedelta

class Simulator(threading.Thread):

    last_run = None
    last_time_interval_update = None

    def __init__(self, dispatcher):
        threading.Thread.__init__(self)

        from allocations import Allocations
        from matcher_queue import MatcherQueue
        from event_matcher import EventMatcher
        from tracker import Tracker
        from matchings import Matchings
        from service_matcher import ServiceMatcher

        queue = MatcherQueue()
        allocations = Allocations()
        tracker = Tracker()
        matchings = Matchings(allocations=allocations,
                              tracker=tracker)
        event_matcher = EventMatcher(queue=queue,
                                     tracker=tracker)
        service_matcher = ServiceMatcher(queue=queue,
                                         tracker=tracker,
                                         matchings=matchings)

        self.dispatcher = dispatcher
        self.event_matcher = event_matcher
        self.service_matcher = service_matcher
        self.time_update_interval = timedelta(milliseconds=env.time_update_interval)
        self.matching_interval = timedelta(minutes=env.matcher_interval)
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
        # time interval update
        # if self.last_time_interval_update is None:
        #     self.last_time_interval_update = datetime.now()
        # if datetime.now() - self.last_time_interval_update > self.time_update_interval:
        #     self.dispatcher.dispatch('time', env.now.isoformat())
        #     self.last_time_interval_update = datetime.now()
        # algorithm run interval
        if self.last_run is None:
            self.last_run = env.now
        # "simulating" running the service matcher at intervals
        # in production this would be some kind of scheduled task
        if env.now - self.last_run > self.matching_interval:
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
        # self.dispatcher.dispatch('time', env.now.isoformat())
        print("Finished matching.")

    def clear_tables(self):
        db_session.query(EventMatching).delete()
        db_session.query(ServiceMatching).delete()
        db_session.commit()

    def run(self):
        self.clear_tables()
        self.simulate()

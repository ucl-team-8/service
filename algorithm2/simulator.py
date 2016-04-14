import env
import threading
from db_queries import db_session
from windowed_query import windowed_query
from models import Trust, GPS, EventMatching, ServiceMatching
from datetime import datetime, timedelta
from utils import date_to_iso, serialize_matchings
from segment import from_matchings_diff

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

        self.matchings = matchings
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
        # algorithm run interval
        if self.last_run is None:
            self.last_run = env.now
        # "simulating" running the service matcher at intervals
        # in production this would be some kind of scheduled task
        if env.now - self.last_run > self.matching_interval:
            self.run_algorithm()
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
        self.run_algorithm()
        print("Finished matching.")

    def clear_tables(self):
        db_session.query(EventMatching).delete()
        db_session.query(ServiceMatching).delete()
        db_session.commit()
        db_session.close()

    def run(self):
        self.clear_tables()
        self.simulate()

    def run_algorithm(self):
        self.service_matcher.run()
        matchings = self.save_matchings_in_global()
        self.dispatcher.dispatch('time', date_to_iso(env.now))
        self.dispatcher.dispatch('matchings', serialize_matchings(matchings))
        for service, unit_matchings_diff in matchings.iteritems():
            if not self.dispatcher.has_listeners(service): continue
            segments = from_matchings_diff(service, unit_matchings_diff)
            self.dispatcher.dispatch_service(service, segments)

    def save_matchings_in_global(self):
        all_matchings = self.matchings.get_all_matchings()
        matchings_diff = self.matchings.get_matchings_diff(all_matchings)
        with env.matchings_lock:
            env.matchings = matchings_diff
        return matchings_diff

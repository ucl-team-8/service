import env
from cache import Cache

class Consumer:

    def __init__(self, matcher):
        self.matcher = matcher
        self.gps_cache = Cache(env.retention_minutes)
        self.trust_cache = Cache(env.retention_minutes)

    def consume_gps(self, gps):

        tiploc = gps.tiploc
        time = gps.event_time

        self.gps_cache.add(tiploc, time, gps)

        close_trust_reports = self.trust_cache.get_within(
                                   tiploc, time, env.within_minutes)

        for trust in close_trust_reports:
            self.matcher.add(trust, gps)


    def consume_trust(self, trust):

        tiploc = trust.tiploc
        time = trust.event_time

        self.trust_cache.add(tiploc, time, trust)

        close_gps_reports = self.gps_cache.get_within(
                                   tiploc, time, env.within_minutes)

        for gps in close_gps_reports:
            self.matcher.add(trust, gps)

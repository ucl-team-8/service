import env
from tiploc_cache import TiplocCache

class EventMatcher:
    """Consumes TRUST & GPS reports. This is where the reports first come from
    the stream.

    Reports that arrive are matched with reports that occurred at the same
    tiploc within a given interval (env.within_minutes). The matchings are added
    to the queue to be processed later by the ServiceMatcher.

    """

    def __init__(self, queue):
        self.queue = queue
        self.gps_cache = TiplocCache(env.retention_minutes)
        self.trust_cache = TiplocCache(env.retention_minutes)

    def match_trust(self, trust):

        tiploc = trust.tiploc
        time = trust.event_time

        self.trust_cache.add(tiploc, time, trust)

        close_gps_reports = self.gps_cache.get_within(
                                   tiploc, time, env.within_minutes)

        for gps in close_gps_reports:
            self.queue.add(trust, gps)


    def match_gps(self, gps):

        tiploc = gps.tiploc
        time = gps.event_time

        self.gps_cache.add(tiploc, time, gps)

        close_trust_reports = self.trust_cache.get_within(
                                   tiploc, time, env.within_minutes)

        for trust in close_trust_reports:
            self.queue.add(trust, gps)

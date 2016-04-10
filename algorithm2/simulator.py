import env
import sqlalchemy
from sqlalchemy import and_, func
from app_db import db
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


# Efficient way to get "slices" of queries without storing the whole result in
# memory.
# Borrowed from SQLAlchemy Usage Recipes:
# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/WindowedRangeQuery

def column_windows(session, column, windowsize):
    """Return a series of WHERE clauses against
    a given column that break it into windows.

    Result is an iterable of tuples, consisting of
    ((start, end), whereclause), where (start, end) are the ids.

    Requires a database that supports window functions,
    i.e. Postgresql, SQL Server, Oracle.

    Enhance this yourself !  Add a "where" argument
    so that windows of just a subset of rows can
    be computed.

    """
    def int_for_range(start_id, end_id):
        if end_id:
            return and_(
                column>=start_id,
                column<end_id
            )
        else:
            return column>=start_id

    q = session.query(
                column,
                func.row_number().\
                        over(order_by=column).\
                        label('rownum')
                ).\
                from_self(column)
    if windowsize > 1:
        q = q.filter(sqlalchemy.text("rownum %% %d=1" % windowsize))

    intervals = [id for id, in q]

    while intervals:
        start = intervals.pop(0)
        if intervals:
            end = intervals[0]
        else:
            end = None
        yield int_for_range(start, end)

def windowed_query(q, column, windowsize):
    """"Break a Query into windows on a given column."""

    for whereclause in column_windows(
                                        q.session,
                                        column, windowsize):
        for row in q.filter(whereclause).order_by(column):
            yield row

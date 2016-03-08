# Creates a new thread that continues fetching the data from a database
# then uses a threadpool every time it 'receives a new event'

# TODO: Update perform action
# TODO: Fix out of bounds error for the last event

import concurrent.futures
import filter_trust
import filter_gps
import threading
import globals
import time
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
from models import *


# This class fetches gps and trust events from the database
# and simulates the realtime environment
class SimulateRealTime(threading.Thread):
    # The speed parameter is how much faster the simulation
    # should go (2 is x2)
    def __init__(self, speed):
        threading.Thread.__init__(self)
        self.speed = speed
        self.records = {'gps': [], 'trust': []}
        self.records['gps'] = self.fetchEvents(GPS, None)
        self.records['trust'] = self.fetchEvents(Trust, None)

    # Fetches the next 100 events from the model
    # since we dont want to store all of the events in the model
    def fetchEvents(self, model, records):
        # If it is a newly declared records
        globals.db_lock.acquire()
        if records is None:
            records = db.session.query(model).\
                order_by(model.event_time.asc()).limit(100)
        else:
            records = db.session.query(model).\
                filter(model.event_time > records[-1]['event_time']).\
                order_by(model.event_time.asc()).limit(100)
        globals.db_lock.release()
        # Extract individual records as dictionary
        return map(lambda x: x.as_dict(), records)

    # If current is a new object, update current
    # else update the next object to contain the
    # data from the report closest to the current
    def closestRecordName(self, current, next):
        other_name = ''
        if current['name'] == 'trust':
            other_name = 'gps'
        elif current['name'] == 'gps':
            other_name = 'trust'
        else:
            if self.records['gps'][0]['event_time'] < self.\
                    records['trust'][0]['event_time']:
                current['name'] = 'gps'
                current['record'] = self.records['gps'][0]
            else:
                current['name'] = 'trust'
                current['record'] = self.records['trust'][0]
            return

        if self.records[current['name']][1]['event_time'] < self.\
                records[other_name][0]['event_time']:
            next['name'] = current['name']
            next['record'] = self.records[current['name']][1]
        else:
            next['name'] = other_name
            next['record'] = self.records[other_name][0]

    # If the length of a record is 0, get the next 100
    # checking if it is equal to one because closestRecordName
    # my need the first element
    def checkEmptyRecords(self):
        if len(self.records['gps']) == 1:
            self.records['gps'].extend(
                self.fetchEvents(GPS, self.records['gps'])
            )
        elif len(self.records['trust']) == 1:
            self.records['trust'].extend(
                self.fetchEvents(Trust, self.records['trust'])
            )

    # Gets the next record and then sleeps the time between the next
    # record and the current record
    # finally deletes the current record and replaces it with next
    def getNextRecordAndSleep(self, executor, current, next):
        self.closestRecordName(current, next)
        time_to_sleep = (
            next['record']['event_time'] - current['record']['event_time']
            ).total_seconds()

        time.sleep(time_to_sleep/self.speed)

        executor.submit(self.performAction, next)
        del self.records[current['name']][0]
        current['name'] = next['name']
        current['record'] = next['record']

    def performAction(self, object):
        # print object['record']
        if object['name'] == 'gps':
            filter_gps.addGPS(object['record'])
        elif object['name'] == 'trust':
            filter_trust.addTrust(object['record'])
        # We don't want threads switching between printing
        # globals.lock.acquire()
        # print globals.segments
        # globals.lock.release()

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=globals.workers) as executor:
            current = {'name': '', 'record': None}
            next = {'name': '', 'record': None}
            self.closestRecordName(current, next)
            executor.submit(self.performAction, current)

            while len(self.records['gps']) > 0 or\
                    len(self.records['trust']) > 0:
                self.checkEmptyRecords()
                self.getNextRecordAndSleep(executor, current, next)

if __name__ == "__main__":
    temp = SimulateRealTime(globals.speedup)
    temp.start()

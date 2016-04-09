from copy import deepcopy
from json import dumps
import globals
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from app_db import socketio

# Returns a json object of a segment
def jsonSegment(segment):
    # We take a deepcopy because we do not want
    # to change the event_time objects in the
    # segment to strings
    segment1 = deepcopy(segment).__dict__
    for match in segment1['matching']:
        if match['gps'] is not None:
            match['gps']['event_time'] = match['gps']['event_time'].strftime('%a, %d %b %Y %H:%M:%S GMT')
        if match['trust'] is not None:
            try:
                match['trust']['event_time'] = match['trust']['event_time'].strftime('%a, %d %b %Y %H:%M:%S GMT')
                match['trust']['origin_departure'] = match['trust']['origin_departure'].strftime('%a, %d %b %Y %H:%M:%S GMT')
            except:
                pass  # Not too sure about why this happens
    return dumps(segment1)


# Emits a message with the appropriate keyword
# keywords are 'update', 'delete' and 'new'
def emitSegment(keyword, segment):
    globals.io_lock.acquire()
    try:
        if keyword == 'delete':  # because it is an id only
            socketio.emit(keyword, segment)
        else:
            json_segment = jsonSegment(segment)
            socketio.emit(keyword, json_segment)
    except IOError:
        pass  # Client disconnected
    finally:
        globals.io_lock.release()

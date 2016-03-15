from sqlalchemy.sql import and_
import globals
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from models import *


# Function that check if a unit was supposed
# to run a service with the headcode
def isPlanned(unit, headcode):
    globals.db_lock.acquire()
    result = db.session.query(Schedule).filter(and_(
        Schedule.unit == unit, Schedule.headcode == headcode
    ))
    globals.db_lock.release()
    try:
        result[0].as_dict()
        return True
    except:
        return False


# Gets the unit from a gps_car_id by querying
# the UnitToGPSMapping table
def getUnitFromCarId(gps_car_id):
    globals.db_lock.acquire()
    result = db.session.query(UnitToGPSMapping).filter(
        UnitToGPSMapping.gps_car_id == gps_car_id)
    globals.db_lock.release()
    try:
        return result[0].as_dict()['unit']
    except:
        return ''


# Gets the diagram_service row for a
# particular unit
def getDiagramServiceByHeadcode(headcode):
    globals.db_lock.acquire()
    result = db.session.query(DiagramService).filter(
        DiagramService.headcode == headcode
    )
    globals.db_lock.release()
    try:
        return result[0].as_dict()
    except:
        return None


# gets the rows from diagram_stop for a particular
# diagram service
def getDiagramStopsByService(diagram_service):
    if diagram_service is None:
        return []
    globals.db_lock.acquire()
    result = db.session.query(DiagramStop).filter(
        DiagramStop.diagram_service_id == diagram_service['id']
    )
    globals.db_lock.release()
    return map(lambda x: x.as_dict(), result)


# Gets all of the diagram stops for a service
def getDiagramStopsByHeadcode(headcode):
    diagram_service = getDiagramServiceByHeadcode(headcode)
    return getDiagramStopsByService(diagram_service)


# Gets the cif_uid from the Schedule using unit and headcode
def cif_uidFromUnitAndHeadcode(unit, headcode):
    globals.db_lock.acquire()
    result = db.session.query(Schedule).filter(and_(
        Schedule.unit == unit, Schedule.headcode == headcode
    ))
    globals.db_lock.release()
    try:
        temp = result[0].as_dict()['cif_uid']
        if temp is None:
            return ''
        return temp
    except:
        return ''


def cif_uidFromHeadcode(headcode):
    globals.db_lock.acquire()
    result = db.session.query(DiagramService).filter(
            DiagramService.headcode == headcode)
    globals.db_lock.release()
    try:
        temp = result[0].as_dict()['cif_uid']
        return temp
    except:
        return None

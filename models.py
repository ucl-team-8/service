from app import db
from sqlalchemy.dialects.postgresql import JSON

class Trust(db.Model):
    __tablename__ = 'trust'
    id = db.Column(db.Integer, primary_key=True)
    headcode = db.Column(db.String(20))
    location = db.Column(db.String(20))
    loc_seq = db.Column(db.Integer)
    arrival_report = db.Column(db.DateTime)
    dep_report = db.Column(db.DateTime)
    planned = db.Column(db.Boolean)
    origin_depart_time = db.Column(db.DateTime)
    CIF_uid = db.Column(db.String(20))
    category = db.Column(db.String(5))

    def __init__(self, headcode, location, loc_seq, arrival_report, dep_report, planned, origin_depart_time, CIF_uid, category):
        self.headcode = headcode
        self.location = location
        self.loc_seq = loc_seq
        self.arrival_report =  arrival_report
        self.dep_report = dep_report
        self.planned = planned
        self.origin_depart_time = origin_depart_time
        self.CIF_uid = CIF_uid
        self.category = category

    def __repr__(self):
        return '<Trust id={0}>'.format(self.id, self.headcode)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(20))
    headcode = db.Column(db.String(20))
    origin_loc = db.Column(db.String)
    origin_dep_time = db.Column(db.DateTime)
    CIF_uid = db.Column(db.String(20))

    def __init__(self, unit, headcode, origin_loc, origin_dep_time, CIF_uid):
        self.unit = unit
        self.headcode = headcode
        self.origin_loc = origin_loc
        self.origin_dep_time = origin_dep_time
        self.CIF_uid = CIF_uid

    def __repr__(self):
        return '<Schedule id={0}>'.format(self.id)

class GPS(db.Model):
    __tablename__ = 'gps'
    id = db.Column(db.Integer, primary_key=True)
    gps_car_id = db.Column(db.String(20))
    event_type = db.Column(db.String(5))
    tiploc = db.Column(db.String(20))
    event_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<GPS id={0}>'.format(self.id)


class UnitToGPSMapping(db.Model):
    __tablename__ = 'unit_to_gps_mapping'
    unit = db.Column(db.String(20), primary_key=True)
    gps_car_id = db.Column(db.String(20))

    def __init__(self, unit, gps_car_id):
        self.unit = unit
        self.gps_car_id = gps_car_id

    def __repr__(self):
        return '<UnitToGPSMapping unit={0}, gps_car_id={1}>'.format(self.unit, self.gps_car_id)

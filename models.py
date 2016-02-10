from app import db
from sqlalchemy.dialects.postgresql import JSON

class Trust(db.Model):
    __tablename__ = 'trust'
    id = db.Column(db.Integer, primary_key=True)
    headcode = db.Column(db.String(20))
    origin_location = db.Column(db.String(20))
    origin_departure = db.Column(db.DateTime)
    tiploc = db.Column(db.String(20))
    seq = db.Column(db.Integer)
    event_type = db.Column(db.String(5))
    event_time = db.Column(db.DateTime)
    planned_pass = db.Column(db.Boolean)

    def __repr__(self):
        return '<Trust id={0} headcode={1}>'.format(self.id, self.headcode)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(20))
    headcode = db.Column(db.String(20))
    origin_location = db.Column(db.String)
    origin_departure = db.Column(db.DateTime)
    cif_uid = db.Column(db.String(20))

    def __repr__(self):
        return '<Schedule id={0} unit={1} headcode={2}>'.format(self.id, self.unit, self.headcode)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class GPS(db.Model):
    __tablename__ = 'gps'
    id = db.Column(db.Integer, primary_key=True)
    gps_car_id = db.Column(db.String(20))
    event_type = db.Column(db.String(5))
    tiploc = db.Column(db.String(20))
    event_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<GPS id={0} gps_car_id={1}>'.format(self.id, self.gps_car_id)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UnitToGPSMapping(db.Model):
    __tablename__ = 'unit_to_gps_mapping'
    unit = db.Column(db.String(20), primary_key=True)
    gps_car_id = db.Column(db.String(20))

    def __repr__(self):
        return '<UnitToGPSMapping unit={0}, gps_car_id={1}>'.format(self.unit, self.gps_car_id)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GeographicalLocation(db.Model):
    __tablename__ = 'geographical_location'
    tiploc = db.Column(db.String(20), primary_key=True)
    stanox = db.Column(db.String(10))
    crs = db.Column(db.String(10))
    description = db.Column(db.String(50))
    easting = db.Column(db.Integer)
    northing = db.Column(db.Integer)
    latitude = db.Column(db.Float(precision=32))
    longitude = db.Column(db.Float(precision=32))
    type = db.Column(db.String(20))
    is_cif_stop = db.Column(db.Boolean)
    cif_stop_count = db.Column(db.Integer)
    cif_pass_count = db.Column(db.Integer)

    def __repr__(self):
        return '<GeographicalLocation tiploc={0}, easting={1}, northing={2}>'.format(self.tiploc, self.easting, self.northing)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DiagramService(db.Model):
    __tablename__ = 'diagram_service'
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(20))
    cif_uid = db.Column(db.String(20))
    date_runs_from = db.Column(db.DateTime)
    date_runs_to = db.Column(db.DateTime)
    days_run = db.Column(db.String(7))
    train_category = db.Column(db.String(2))
    train_class = db.Column(db.String(1))

    def __repr__(self):
        return '<DiagramService unit={0}'.format(self.unit)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class DiagramStop(db.Model):
    __tablename__ = 'diagram_stop'
    id = db.Column(db.Integer, primary_key=True)
    diagram_service_id = db.Column(db.Integer, db.ForeignKey('diagram_service.id'), nullable=False)
    diagram_service = db.relationship('DiagramService', backref='diagram_stop')
    station_type = db.Column(db.String(2)) # LO (origin), LI (intermediate), LT (terminating) and CR (changes en route)
    tiploc = db.Column(db.String(20))
    arrive_time = db.Column(db.DateTime) # these are the scheduled times (not public)
    depart_time = db.Column(db.DateTime)
    pass_time = db.Column(db.DateTime)
    engineering_allowance = db.Column(db.Integer)
    pathing_allowance = db.Column(db.Integer)

    def __repr__(self):
        return '<DiagramStop diagram_service_id={0}, tiploc={1}'.format(self.diagram_service_id, self.tiploc)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

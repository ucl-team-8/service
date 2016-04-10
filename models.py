from app_db import db


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

db.Index('trust_service_lookup',
         Trust.headcode,
         Trust.origin_location,
         Trust.origin_departure)


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
    gps_car_id = db.Column(db.String(20), index=True)
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
    headcode = db.Column(db.String(20))
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
    station_type = db.Column(db.String(2))  # LO (origin), LI (intermediate), LT (terminating) and CR (changes en route)
    tiploc = db.Column(db.String(20))
    arrive_time = db.Column(db.Time)  # these are the scheduled times (not public)
    depart_time = db.Column(db.Time)
    pass_time = db.Column(db.Time)
    engineering_allowance = db.Column(db.Integer)
    pathing_allowance = db.Column(db.Integer)

    def __repr__(self):
        return '<DiagramStop diagram_service_id={0}, tiploc={1}'.format(self.diagram_service_id, self.tiploc)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class EventMatching(db.Model):
    __tablename__ = 'event_matching'
    id = db.Column(db.Integer, primary_key=True)

    # Service identifier
    headcode = db.Column(db.String(20))
    origin_location = db.Column(db.String(20))
    origin_departure = db.Column(db.DateTime)

    # Rolling stock identifier
    gps_car_id = db.Column(db.String(20))

    # References to the actual events
    trust_id = db.Column(db.Integer, db.ForeignKey('trust.id'), nullable=False)
    gps_id = db.Column(db.Integer, db.ForeignKey('gps.id'), nullable=False)
    trust = db.relationship("Trust")
    gps = db.relationship("GPS")

    # Time difference between trust & gps
    time_error = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<EventMatching headcode={0}, origin_location={1}, gps_car_id={2}'.format(self.headcode, self.origin_location, self.gps_car_id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

event_matching_service_index = db.Index('event_matching_service_lookup',
         EventMatching.headcode,
         EventMatching.origin_location,
         EventMatching.origin_departure)

event_matching_unit_index = db.Index('event_matching_unit_lookup',
         EventMatching.gps_car_id)

class ServiceMatching(db.Model):
    __tablename__ = 'service_matching'

    # Note composite primary key below, since we only want a single matching for
    # a service and unit

    # Service identifier
    headcode = db.Column(db.String(20), primary_key=True)
    origin_location = db.Column(db.String(20), primary_key=True)
    origin_departure = db.Column(db.DateTime, primary_key=True)

    # Rolling stock identifier
    gps_car_id = db.Column(db.String(20), primary_key=True)

    total_matching = db.Column(db.Integer, nullable=False)
    median_time_error = db.Column(db.Float, nullable=False)
    variance_time_error = db.Column(db.Float, nullable=False)

service_matching_service_index = db.Index('service_matching_service_lookup',
         ServiceMatching.headcode,
         ServiceMatching.origin_location,
         ServiceMatching.origin_departure)

service_matching_unit_index = db.Index('service_matching_unit_lookup',
         ServiceMatching.gps_car_id)

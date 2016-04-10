

class Matcher:

    def __init__(self):
        self.queue = set()

    def add(self, trust, gps):

        item = (trust.headcode,
                trust.origin_location,
                trust.origin_departure,
                gps.gps_car_id)

        self.queue.add(item)

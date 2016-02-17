from math import sin, cos, sqrt, atan2, radians


def calculateDist(coord1, coord2):
    # approximate radius of earth in km
    R = 6373.0
    
    coord1['latitude'] = radians(coord1['latitude'])
    coord1['longitude'] = radians(coord1['longitude'])
    coord2['latitude'] = radians(coord2['latitude'])
    coord2['longitude'] = radians(coord2['longitude'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

from math import sqrt, floor, ceil
from collections import defaultdict
from datetime import datetime

# datetime difference in seconds
def diff_seconds(a, b):
    return (a - b).total_seconds()

def average(lst):
    return sum(lst) / len(lst)

## {{{ http://code.activestate.com/recipes/511478/ (r1)
def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = floor(k)
    c = ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def median(lst):
    lst = sorted(lst)
    return percentile(lst, 0.5)

def iqr(lst):
    lst = sorted(lst)
    return percentile(lst, 0.75) - percentile(lst, 0.25)

def variance(lst):
    avg = average(lst)
    return sum((avg - value) ** 2 for value in lst) / len(lst)

def stddev(list):
    return sqrt(variance(lst))

def combine_stats(a, b):
    """Combines the mean and variance for two samples"""

    m, mean_m, var_m = a
    n, mean_n, var_n = b

    t_m = mean_m * m
    t_n = mean_n * n

    total = m + n
    mean = float(t_m + t_n) / (total)

    s_m = var_m * m
    s_n = var_n * n

    s_mn = s_m + s_n + (float(m) / (n * (total))) * ((float(n) / m) * t_m - t_n) ** 2

    variance = float(s_mn) / total

    return (total, mean, variance)

# http://stackoverflow.com/a/3721301/1775517
def time_intervals_overlap(t1start, t1end, t2start, t2end):
    return (t1start <= t2start <= t1end) or (t2start <= t1start <= t2end)

def get_interval_overlap(t1start, t1end, t2start, t2end):
    minutes = min(t1end - t2start, t2end - t1start).total_seconds() / 60
    return minutes if minutes > 0 else 0

def pkey_from_service_matching(service_matching):
    return (service_matching.headcode,
            service_matching.origin_location,
            service_matching.origin_departure,
            service_matching.gps_car_id)

def pkey_from_service_matching_props(service_matching_props):
    return (service_matching_props['headcode'],
            service_matching_props['origin_location'],
            service_matching_props['origin_departure'],
            service_matching_props['gps_car_id'])

def flip_matchings(matchings):
    """Converts between unit matchings and service matchings."""
    converted = defaultdict(set)
    for key, values in matchings.iteritems():
        for value in values:
            converted[value].add(key)
    return dict(converted)

def date_to_iso(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')

def iso_to_date(string):
    return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')

def serialize_matchings(matchings_diff):
    json = list()
    for service, units in matchings_diff.iteritems():
        headcode, origin_location, origin_departure = service
        json.append({
            'headcode': headcode,
            'origin_location': origin_location,
            'origin_departure': date_to_iso(origin_departure),
            'units': { key: list(units) for key, units in units.iteritems() }
        })
    return json

def get_service_key(service_dict):
    origin_departure = service_dict['origin_departure']
    if not isinstance(origin_departure, datetime):
        origin_departure = iso_to_date(origin_departure)
    return (service_dict['headcode'],
            service_dict['origin_location'],
            origin_departure)

def get_service_dict(service_key):
    return {
        'headcode': service_key[0],
        'origin_location': service_key[1],
        'origin_departure': service_key[2]
    }

def get_matching_key(matching_dict):
    return get_service_key(matching_dict) + (matching_dict['gps_car_id'], )

def flatten(lst):
    return [item for sublist in lst for item in sublist]

from math import sqrt, floor, ceil

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

# datetime difference in seconds
def diff_seconds(a, b):
    return (a - b).total_seconds()

def average(lst):
    return sum(lst) / len(lst)

def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
        return None
    if len(lst) % 2 == 1:
        return lst[((len(lst)+1)/2)-1]
    else:
        return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1])) / 2.0

def variance(lst):
    avg = average(lst)
    return sum((avg - value) ** 2 for value in lst) / len(lst)

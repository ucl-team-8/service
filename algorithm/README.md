# How does the algorithm work?

## Simulating realtime
The [simrealtime.py](algorithm/simrealtime.py) file creates a new thread that simulates a real time environment by querying the database for trust and gps reports and calling the appropriate functions when it gets a new report.

Currently you can test the algorithm by running:
```
python algorithm/simrealtime.py
```

This will print out the segments after every change that has happened.

## Segments
What the algorithm currently does is creating segments from all of the reports that are coming in.
We define a segment to be a a set of consecutive gps reports, with their matching trust reports. However the gps and trust reports in one given segment can only be from 1 rolling stock and service respectively.

The data structure of a segment can be found in [globals.py](algorithm/globals.py). At the moment, all of the segments are stored in memory but eventually they will be stored in the database.

These are all of the data structures:

**Segment:**
- unit - *String*
- cif_uid - *String*
- gps_car_id - *String*
- headcode - *String*
- matching - *Array of Dictionaries*
    - gps - *gps_report*
    - trust - *trust_report*
    - dist_error - *Int*
    - time_error - *datetime.timedelta*


**Trust Report:**
- id - *Int*
- headcode - *String*
- event_time - *datetime.datetime*
- event_type - *String*
- origin_departure - *datetime.datetime*
- origin_location - *String*
- planned_pass - *Bool*
- seq - *Int*
- tiploc - *String*


**GPS Report:**
- id - *Int*
- event_type - *String*
- tiploc - *String*
- event_time - *datetime.datetime*
- gps_car_id - *String*


## Constructing segments
There are 2 main files that are responsible for creating the segments: [filter_gps.py](algorithm/filter_gps.py) and [filter_trust.py](algorithm/filter_trust.py). Both add or change segments using a different algorithm.

The functions in [filter_gps.py](algorithm/filter_gps.py) and [filter_trust.py](algorithm/filter_trust.py) are executed by a threadpool.

### Adding gps reports to a segment
1. Goes through the segments and finds the most recent one with the same gps_car_id.
2. Goes through all of the matching events in that segment and checks if there is potential trust report, that has no match.
3. It filters those potential trust reports to see if any are within a given tolerance, if there are, it adds the gps report to that trust report.
4. Else if there is no trust report:
  1. If there is no potential segment, it adds a new one, containing the gps report.
  2. Else it adds the gps report to that segment.

## Adding trust reports to a segment
1. Goes through the segments and filters out the ones that either have the same headcode as the report or the ones that don't have a headcode yet.
2. In all of those segments, the algorithm looks at the gps reports, that don't have a match yet. Then we filter out the segments that contain a potential match for the trust report.
3. Another filtering layer, then looks at the unit code of the segment and the headcode of the trust report and checks if that rolling stock was supposed to run the service according to the genius allocations.
4. From those filtered segments, it chooses the one with the most matches and the most amount of times that 'seq' is respected.
  1. If it does not find a segment, it creates a new one, containing the trust report.
  2. Else it looks through all of the gps reports that don't have a matching trust report yet. Then it chooses one, depending on the tolerance and if it respects the 'seq' field.

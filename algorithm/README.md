# How does the algorithm work?

## Simulating realtime
The [simrealtime.py](algorithm/simrealtime.py) file creates a new thread that simulates a real time environment by querying the database for trust and gps reports and calling the appropriate functions when it gets a new report.

Currently you can test the algorithm by running:
```
python algorithm/simrealtime.py
```

This will print out the segments after every change that has happened.

The realtime thread then creates a threadpool and, which it uses to do all of the data processing. 

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
- isPlanned - *Bool*
- remove - *Bool*  
- matching - *Array of Dictionaries*
    - supposed_to_run: *Bool*
    - gps - *gps_report*
    - trust - *trust_report*
    - dist_error - *Int*


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
- predicted - *Bool* // If the event was supposed to happen according to the schedule


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

### Adding trust reports to a segment
1. Goes through the segments and filters out the ones that either have the same headcode as the report or the ones that don't have a headcode yet.
2. In all of those segments, the algorithm looks at the gps reports, that don't have a match yet. Then we filter out the segments that contain a potential match for the trust report.
3. Another filtering layer, then looks at the unit code of the segment and the headcode of the trust report and checks if that rolling stock was supposed to run the service according to the genius allocations.
4. From those filtered segments, it chooses the one with the most matches and the most amount of times that 'seq' is respected.
  1. If it does not find a segment, it creates a new one, containing the trust report.
  2. Else it looks through all of the gps reports that don't have a matching trust report yet. Then it chooses one, depending on the tolerance and if it respects the 'seq' field.


### Overall view
Separating how we add gps and trust reports, might not give you the entire picture. Hence, this part should explain the overarching idea.


There will be a lot more gps reports than trust reports. Therefore most of the time, the algorithm will add gps reports to an existing segment without finding a matching trust report. The way that it does this is by first finding the segment, with the same headcode and the most recently added gps report.


For instance if we have two segments, each with a gps_car_id '15068'. The first segment represents the time when the rolling stock ran service '1A02' and the second segment represents the service that it is currently running. We want to add the newest report to the segment that the rolling stock is currently running and we select it by finding the segment with the most recently added gps report.


However we want to create another segment as soon as that rolling stock starts running another service. Which is why it also looks for segments, with no gps_car_id and see if it can match the gps report to the existing trust report(s) in that segment. If it can, it will add the gps report to that segment. Otherwise, it will look for a matching trust report in the previously found segment and add the report to it.


There are some other special cases where for example it does not find a potential segment. In those cases, the algorithm will often create a new segment. This is often found when for example a rolling stock starts running.


There are some other special cases where for example it does not find a potential segment. In those cases, the algorithm will often create a new segment. This is often found when for example a rolling stock starts running.


At the same time, we continue to receive trust reports. In the beginning, we do some very similar processing. We go through the segments and filter out the ones with the same headcode as a report. However if we do not find one, that is an indication that this service just started running. In this case, we either look for a segment that does not have a headcode yet and look for a potential matching gps report. If we find a potential match, we add the trust report to that segment. But if we do not find one,
we simply create a new segment.


However what happens most of the time is that we get a set of segments that have the same headcode. This should be a relatively small set so we can permit to look through the matching array and filter out sets that do not have any potential matching gps reports.


We know that it is more likely for a service be run by the rolling stock that was specified by the genius allocation. Hence, we prefer segments with the same gps_car_id as the rolling stock that was supposed to run the service.


If we still have more than one segment in the set, which is highly unlikely, we need another way of choosing one above the other. The way we decided to do this is by giving a preference to the segment with the most amount of matches.
For instance if we look at the figure below, red and blue represent two potentially matching segments. Imagine we are currently processing the overlapping trust report. We would prefer the red one by comparing the amount of matching trust report the red and the blue rolling stock already have. Additionally, to be sure we also analyse the amount of times both segments respect the seq value.

![figure 1](../static/images/readmefig1.png)

All of the above constructs the segments to a reasonable extent however we still need to go over some of the segments and check if we could potentially improve them.

## Interpolating

After we have inserted a trust report, we also perform what we identify as interpolating. It means that we go over a certain amount of segments and try to increase their accuracy.


First, the algorithm goes over the segments with the same unit code and tries to join them together. For instance if we look at figure 2 below, we can see 3 segments. Each segment is represented by an arrow. The colour of the arrow represents the gps_car_id and the circles represent the trust reports. 

We can see that in the middle, there is a very short segment with only 1 stop and the two other (outer) segments have multiple stops and have the same gps_car_id. Looking at the diagram, we know that it is very likely that we can combine all three segments into one segment with the same gps_car_id as the first and the last segment. This is exactly what the first step of interpolation does.

![figure 2](../static/images/readmefig2.png)

The second step then checks if there are any segments, without a headcode yet that might be running the same service as another rolling stock. If it finds such a segment, it adds all of the matching trust report to the appropriate gps reports.
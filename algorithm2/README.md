SIMPLEST ALTOGRTIHM EVER. NO ALGORTIHM CAN BE SIMPLER.

#### Excuses (sort of)

I don't really know where to start. I ended up changing so many things, but we _should_ be able to revert to the old algorithm if we need to. I know this is probably not the best time to be changing the whole thing and I started this not really intending to. But anyway.

#### What's left to do

The results it produces are OK, but can be much better with some tweaks. The big thing left to do is to figure out how to determine whether a matching is **good enough** and that the unit really ran the given service. I think there is enough data calculated to be able to make a good decision, but I don't know what the criteria for a "good decision" are.

---

## How the algorithm works

The algorithm runs in a single thread separate from the **app** thread. The thread is started by the simulator. The big, heavyweight, final pass matching algorithm executes in intervals (currently set to 30min in simulated time).

Much like the previous algorithm, the **simulator** gets events from the database and passes them on. Compared to the old one, there is no speedup factor, the simulator always gets and processes whatever the next event is, so effectively "simulated time" is not linear but is dictated by the "spacing" between events. This way, the algorithm runs and terminates as quickly as it possibly can.

The simulator passes the events onto the **event_matcher**. The event_matcher keeps a **cache** of all events (reports) that occurred within 30min at every tiploc (2 separate caches, trust & gps). It matches up trust and gps events that occurred at the same tiploc within 5min of one another. (If a trust event arrives, it searches the gps cache and matches it up with events within 5min, and vice versa.) The event_matcher also records how events occurred from a specific service or a gps_car_id in the **tracker**. The tracker additionally records when an event was first and last seen from a service/gps_car_id. (This avoids querying the Trust table for the data.)

The event_matcher records the matchings of two events in the **queue**. (Btw, the events were instances of database models so far.) The queue stores the matchings as a dictionary containing all the fields of an **EventMatching** (database model), ready to be bulk inserted into the database.

*.....YAAAAAWWN*

I'll finish this later.

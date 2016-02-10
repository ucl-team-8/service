import d3 from "d3";
import _ from "lodash";

var data = window.data || {};

function loadData() {
	return new Promise(function(resolve, reject) {
	    d3.json("/events/trust.json", function(err, trustData) {
	      d3.json("/events/gps.json", function(err, gpsData) {
	        d3.json("/data/schedule.json", function(err, scheduleData) {
	        	if(!_.some([trustData, gpsData, scheduleData], function(d) {return typeof d == 'undefined';})) {
			        data.trustData = trustData.result;
			        data.gpsData = gpsData.result;
			        data.scheduleData = scheduleData.result;
			        resolve(data);
	        	}
	        	else {
	        		reject("Data did not all load");
	        	}
	        });
	      });
	    });
	});
}

loadData().then(function(data) {
	processData(data);
	console.log(data);
}).catch(function(reason) {
	console.log(reason);
});

function processData(data){
	_.forEach(data.trustData, function(d, i, c) {
		d.event_time = new Date(d.event_time);
		d.origin_departure = new Date(d.origin_departure);
		d.tiploc = d.tiploc.trim();
	});

	data.trustData = d3.nest()
	    .key(d => d.headcode)
	    .sortValues((a, b) => d3.ascending(a.seq, b.seq))
	    .key(d => d.gps_car_id).sortKeys(d3.ascending)
	    .entries(data.trustData);

	_.forEach(data.gpsData, function(d) {
		d.event_time = new Date(d.event_time);
	});

	data.gpsData = d3.nest()
	    .key(d => d.gps_car_id)
	    .sortKeys(d3.ascending)
	    .sortValues((a,b) => d3.ascending(a.event_time, b.event_time))
	    .entries(data.gpsData);

	_.forEach(data.scheduleData, function(d) {
		d.origin_departure = new Date(d.origin_departure);
	});
}

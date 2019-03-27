# Commuting in Boston

## Why

Commuting in Boston hits close to home for me - I commute every day from home to school. I feel bad for driving every day but from where I live there's no better alternative. I would rather take public transit or a carbon neutral alternative like biking, but it's too inconvenient. Factors like traffic, the weather, and distances play a role.

In this project I try to derive some new knowledge about commuters using boston data. This includes data about universities in Boston, bike sharing programs, and the trains. I'll go into more detail about the datasets I derive below.

In this project I'll investigate a few questions, including:

* Students take bikeshare bikes to school - where are they coming from?
* Weather impacts bicycling in Boston, but to what extent?
* Does the weather similarly impact the trains in Boston?

## Data Portals and Datasets

Here are the portals and datasets I used

* Data.boston.gov
	* Universities in Boston
* BlueBike
	* System data (all 1.7 million rides of 2018)
* NOAA
	* Boston Weather 2018
* MBTA
	* Train routes
	* Past live alert notices

## (Non-trivial) Derived Datasets

I have found three important datasets.

First, the rides_and_weather dataset (db.kgarber.rides_and_weather). This dataset uses the weather dataset and the BlueBike dataset to quantify what we might think is clear - the colder it is outside, the less people use bikesharing and the shorter their rides are. The dataset is 10 degree buckets (0-10, 10-20, etc), and shows the average number of rides in the day as well as the average duration of a ride.

Second is the university_bluebike_stations dataset (db.kgarber.university_bluebike_stations). It combines the BlueBike dataset as well as the university dataset to tell us an important piece of information: for each university, from where are people commuting to it? For BU for example, the most popular station to leave in order to arrive at BU is not surprisingly Packard's Corner. 

The dataset includes information for all universities of greater than 500 students, shows which BlueBike stations are near these unis (using a mongo geographical search), and shows from where people ride to the university by doing a search for 7AM - 11AM weekday rides (most popular departure stations).

The third and final derived dataset, alerts_and_weather, takes a look at the Green, Red, Orange, and Blue line in Boston, and tells us how many alerts there are for Boston Trains on an average day in different temperatures. I was curious to see if particularly cold weather caused lots of delays. This dataset uses the alerts, routes, and weather datesets.

## Files

All python files with "download_" prepended are responsible for downloading the data from the various data portals, the internet, and datamechanics.io. 

`alerts_and_weather.py` generates the alerts_and_weather dataset. `rides_per_day.py` creates an intermediary dataset of the number of BlueBike rides per day, it is not one of my final three datasets. `rides_and_weather.py` creates the rides_and_weather dataset. `university_bluebike_stations.py` creates the dataset of bluebike stations near universities as well as from where people ride to them.

## Running

If you configure your `auth.json` as described below, simply writing `python execute.py kgarber` from the root directory of the repository should run all of the scripts in the required order, and generate the provenance document.

## auth.json

The auth.json file should have a key to access the MBTA data. A free and unprotected key is listed below because the MBTA provides it as a developer key which may be removed at any time but works as of writing this.

```
{
	"services": {
		"mbta": {
			"service": "MBTA",
			"dev-API-key": "wX9NwuHnZU2ToO7GmGR9uw"
		}
	}
}
```

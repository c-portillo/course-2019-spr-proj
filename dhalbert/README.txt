Project 1: Declan Halbert

For this project my goal was to determine if people living in higher crime rate areas in Boston don't have the opportunity to use Hubway. To do this, I used the following datasets.
	- Hubway Stations
	- MBTA Stations
	- Bluebike (Hubway) Statistics
	- Crime rate statistics in Boston
	- Traffic lights in boston

I began by merging the data sets of the Hubway Stations and MBTA Stations to determine how far away they were from eachother. Next, I merged the traffic lights with that data set to get an estimate on the amount of traffic coming through.
Next, I merged the Bluebike data with the MBTA Stations to see which Bluebike stations had no bikes. After that, I took the crime data and cut it down to only list the ROBERY type of crime along with the time of day.

At the end of Project 1 I have three main datasets:
	- mbta_station (Hubway Stations merged with MBTA Stations and Traffic Lights)
	- bluebike_station (Empty Bluebike racks merged with MBTA Stations)
	- crime_fixed (the crimes commited in Boston (only ROBBERY))

Further work can be done on this by:
	- merging all three datasets
	- comparing coordinates on that merged dataset to see which stations are affected by crime the most
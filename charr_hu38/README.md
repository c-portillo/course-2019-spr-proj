# Comparing Recreational Bike Use by Population for 4 Major Cities

## Summary

Our goal was to determine how much time people in different cities spend biking for pleasure.  We decided to use publicly 
available data sets for major bike rental companies for 4 cities to determine how much time was spent renting bikes.  We chose
Chicago, NYC, Washington DC, and Chattanooga (as a control group for a smaller city), and picked a recent month with data
available for all 4 cities (2018-09).  As the 4 cities had moderately different schemas and range of information, we had to
parse the data using selections and projections to add them into our DB in a format of 4 tables (ObjectID, Duration, Month).
We added a field for month so that we could easily select the data pertinent to our required window.  We then aggregated the
total time spent on bikes for these 4 datasets and combined them to form a new data set of the form (ObjectID, City,
TotalDuration).  We treated the aggregations as 1 unique transformation and the union as a second.  We then joined this
with our 5th dataset, which included census data on all American cities, to create a final data set of the form 
(ObjectID, City, TotalDuration, Population) to give us an idea of the ratio between time spent on bikes vs population to 
determine which cities utilized rental bikes more.

## Data Sets
- Chicago Bike Data
- New York City Bike Data
- Washington Bike Data
- Chattanooga Bike Data
- Census Data

While the first 4 data sets contain similar information, they were made available in various methods including zipped CSV's
and JSON.  They also had varying schemas, which necesitated different code to parse each.

## Transformations
- Sum Aggregation for each City's Bike Data
- Union of the 4 Sum Aggregations
- Join of the bike data aggregation and census data for each city
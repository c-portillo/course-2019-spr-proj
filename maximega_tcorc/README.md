Data Sets Used:

  https://api.datausa.io/api/?sort=desc&show=geo&required=income&sumlevel=tract&year=all&where=geo%3A16000US3651000
  http://datamechanics.io/data/maximega_tcorc/NYC_census_tracts.csv
  http://datamechanics.io/data/maximega_tcorc/NYC_subway_exit_entrance.csv
  https://data.cityofnewyork.us/resource/swpk-hqdp.json     
  https://data.cityofnewyork.us/resource/q2z5-ai38.json
  
Data Portals Used:

   https://data.cityofnewyork.us/       
   https://datamechanics.io/       
   https://datausa.io       
   
Non-trivial Data Transformations:

  1: Merging economic with geographical census information, creating a new data set that has a census tract as a key and (average income per tract, neighborhood that the tract belongs to, and multipolygon coordinates) as a value.
  
  2: Merging subway station information with neighborhood (NTA) information, creating a new data set that has an NTA code as a key and (multipolygon coordinates, and (station name, subway line, and coordinates (lat, long) of the station) as a value.
  
  3: Merging neighborhood population information with (2), creating a new data set that has an NTA code as a key, and (name, multipolygon coordinates, station information, and population) as a value.
 
  4: Merging (1) with (3), creating a new data set that has an NTA code as a key, and a (name, station information, and population, and census information) as a value.
  
Problem to Solve:
  
  The subway is an essential mode of transportation in New York City. Life in NYC has gotten far more expensive, and the subway is no exception; a ride fare has increased 37.5% (from $2.00 to $2.75) in the last 16 years. To help make life more affordable, we thought it could be worthwhile to rethink subway fares. Taking the London Underground zoning system as an example, we thought that maybe NYC subways could benifit from fare zones. In London the cost of a subway ride depends on the distance of your travel (how many zones you cross). We thought that we could rezone the subway system, but instead of creating zones based on distance, we would create fare zones based on socio-economic data from each NYC neighborhood (NTA). In the future, we may also like to look deeper into the volume and type of travel on (busses, taxi, ubers, etc...) vs subways, and the most frequent routes taken by subway riders. The goal would be for people from less afluent neighborhoods pay less for a subway swipe than those from more affluent neighborhoods, all while ensuring that the MTA would not lose money in this venture. 


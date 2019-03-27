
# Dyanmic Chicago Transit Fares
Nathaniel Smith | BU: smithnj | github: njsmithh </br>
CS504 - Data Mechanics - Project 1

## Proposal
The City of Chicago is the third largest city in the United States. Like other urban areas, it has a relatively robust transit network connecting the city and the surrounding suburbs. The Chicago Transit Authority ('CTA') is tasked with management of the Chicago bus and the elevated-rail ('L') networks. It opts for a static fare, independent of distance traveled within the network and other possible variables unlike a city such as London, which has designated zones for determining fare. The Metra commuter rail, which serves the greater Northwestern Illinois area, does use a distance-based fare. But what if the CTA took an approach similar to Metra rail, but also taking into account "surge" style pricing (with congestion and ridership data) and while maintaining a more stable price for transit in lower-income areas?

## Data Sets

| Portal              | Dataset                                                                                                                                            | Notes                                             |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| datamechanics.io | ['L' Station Ridership Stats](http://datamechanics.io/data/smithnj/smithnj/CTA_Ridership_Totals.csv)                | Retrieved as .csv                                |
| Chicago Data Portal | [Chicago Community Areas](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Neighborhoods/bbvz-uum9)                        | Retrieved as .geojson                                |
| Chicago Data Portal | [Census Socioeconomic Hardship](https://data.cityofchicago.org/Health-Human-Services/Census-Data-Selected-socioeconomic-indicators-in-C/kn9c-c2s2) | Retrieved as .json                                |
| Data.gov            | [Chicago Congestion](https://catalog.data.gov/dataset/chicago-traffic-tracker-congestion-estimates-by-regions-a7daf)                     | Retrieved as .csv                                |
| datamechanics.io    | ['L' Station Locations](http://datamechanics.io/?prefix=smithnj/)                                                                                  | Retrieved as .klm, manually converted to .csv |
## Transformations
Transformations should point to reducing/projecting data in a way to determine price for all L stations on a certain day, such as Weekday, Weekend, or Holiday.
1. **create_travelstats**: Utilizes pandas library to aggregate ridership sums per station per month [aggregation]. A four year average is calculated after using the ridership sums [projection].

    This can point to calculating whether or not a station should expect to be busy on a certain type of day (weekday, weekend, holiday) and adjust pricing accordingly.
2. **create_communitydata**: Utilizes pandas and geopandas libaries to merge census socioeconomic hardship data and geospatial data for each specific Community Area Number [union] and drops [projection] unutilized census data.

    Chicago uses Community Area Numbers as a way to identify specific regions. By joining these two databases, socioeconomic hardship is now linked with geospatial data of the neighborhood, which can lead to determining hardship of the area surrounding an L-station.
    
3. **create_mergedstations**: Utilizes geopandas libary to merge two distinct types of geospatial data: point and multipolygon. Points in Chicago L-station date are mapped onto [projection] the Chicago Community Area Numbers dataset.

---
#### Library Dependencies
* pandas, geopandas
* JSON
* Data Mechanics Library, Provenance, Protoql
* datetime
* spatialindex
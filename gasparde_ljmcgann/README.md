Presenting the Relationships Between Neighborhoods, Crime and, Health Choices.
=============================================================================
 Team: Gaspard Etienne (gasparde) & Leo McGann (ljmcgann)
---------------------------------------------------------------------
Why?
-----------------------------------------------------------------------------
Given some of the data sets we found we wanted to show if there was some relationships we could derive from associating neighborhoods, crime data provided by the city of boston, health data on measures of chronic disease related to unhealthy behaviors, property values, and service request to the boston government by residents on problems they perceive in their city. 

Datasets and Data Portals 
-------------------------------------------------------------------------------

##### CRIME INCIDENT REPORTS (AUGUST 2015 - TO DATE) (SOURCE: NEW SYSTEM)

A dataset containing crime reports reported by the city of boston.

https://data.boston.gov/datastore/odata3.0/12cb3883-56f5-47de-afa5-3b1cf61b257b

##### PROPERTY ASSESSMENT

This data set determines the value of property in Boston. It provides address value,  living area and the total value of properties.

https://data.boston.gov/dataset/e02c44d2-3c64-459c-8fe2-e1ce5f38a035/resource/fd351943-c2c6-4630-992d-3f895360febd/download/ast2018full.csv

##### 311 SERVICE REQUESTS

The 311 service is provided by the city of boston to request or report non emergency issues and the data set contains all theses request. 

https://data.boston.gov/dataset/8048697b-ad64-4bfc-b090-ee00169f2323/resource/2968e2c0-d479-49ba-a884-4ef523ada3c0/download/tmpl_0f_20n.csv

##### BOSTON NEIGHBORHOODS

The Neighborhood boundaries data layer is a combination of zoning neighborhood boundaries, zip code boundaries and 2010 Census tract boundaries.

http://bostonopendata-boston.opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.geojson


##### 500 Cities: Local Data for Better Health, 2018 release

This dataset includes 2016, 2015 model-based small area estimates for 27 measures of chronic disease related to unhealthy behaviors (5), health outcomes (13), and use of preventive services (9)

https://chronicdata.cdc.gov/api/views/6vp6-wxuq/rows.csv


Data Transformation
--------------------------------------------------------------------------------
* The first transformation use the property assessment data set and calculate the price of living  and then places tries to get the location of the property by geocoding the addresses given in the table.

* The Second transformation calculates the amount of time each request in the data set is overdue by if they are, it then takes their locations so that it can place them on a map to see which neighborhoods the are place in and which neighborhood has the highest average of overdue time.

* The third transformations takes the neighborhood shape file and assign crimes for the the crime data set and health data set to neighborhoods. from the all these we wish to see if neighborhoods with lower property values or poorer neighborhoods have more crime, less response to non emergency request, and higher chronic disease related to unhealthy behaviors.





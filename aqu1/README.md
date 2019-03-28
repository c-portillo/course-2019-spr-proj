## Question: 
  How does proximity to public schools and colleges as well as education attainment affect the disparity in wealth across different communities in Boston? How can the city of Boston optimize public transportation stops to provide people with low income access to education?

## Project Description: 
  Boston is home to many groups of people of different socioeconomic statuses. We are interested in how different factors such as proximity to the nearest schools and education attainment affect the economic demographics of neighborhoods throughout Boston. For residents with low income, there is also the issue of having access to efficient public transportation to obtain an education. Currently, the city has bus and train routes set up to serve the different neighborhoods. We are interested in how the placement of these routes are currently serving the lower-income populations of Boston compared to higher-income populations and how train and bus stops can be optimized to serve all populations equally in order to aid in access to education. We have sourced data from ArcGIS Hub on the location of bus and train stops. We also have data from the Boston Data Portal on education attainment for people ages 25+ throughout the different neighborhoods of Boston. Lastly, Boston Open Data has provided data regarding information on vulnerable populations in Boston as well as the locations of all public schools and colleges within the city. 

## Datasets

Colleges and Universities within the City of Boston: 
http://bostonopendata-boston.opendata.arcgis.com/datasets/cbf14bb032ef4bd38e20429f71acb61a_2.csv

Boston Public Schools for 2018-2019: 
http://bostonopendata-boston.opendata.arcgis.com/datasets/1d9509a8b2fd485d9ad471ba2fdb1f90_0.csv

Educational Attainment Demographics by Neighborhood from 1950 to 2010: 
https://data.boston.gov/dataset/8202abf2-8434-4934-959b-94643c7dac18/resource/bb0f26f8-e472-483c-8f0c-e83048827673/download/educational-attainment-age-25.csv

Information on Vulnerable Populations Throughout Boston (Low Income, People With Disabilities, People of Color, etc) from 2008-2012: 
http://bostonopendata-boston.opendata.arcgis.com/datasets/34f2c48b670d4b43a617b1540f20efe3_0.csv

MBTA Bus Stops: 
https://opendata.arcgis.com/datasets/2c00111621954fa08ff44283364bba70_0.csv?outSR=%7B%22wkid%22%3A102100%2C%22latestWkid%22%3A3857%7D

MBTA T-Stops:  
http://maps-massgis.opendata.arcgis.com/datasets/a9e4d01cbfae407fbf5afe67c5382fde_2.csv

## Transformations: 

1. First we created a new income dataset containing the percent of people who were low income across each neighborhood in Boston. First, we aggregated all of the data across the tract codes for each of the 23 neighborhoods (each neighborhood has multiple tract codes). Then, we applied a projection to create a new column for the proportion of people who are low income (people who were 100% below the poverty level and those who were 100–149% of the poverty level).

2. A new dataset for educational attainment for people ages 25+ throughout the different neighborhoods of Boston was created by first filtering for data in the 2000s decade. Data from the 2010s decade was not used because there was no data in the 2010s decade. A  projection was then applied to remove the ‘%’ at the end of the values in the percent of population column in order to make calculations easier in the future.

3. A new dataset containing all of the MBTA bus and train stops was created to include all of the latitude and longitudes of all MBTA bus and T stops. First, the latitude and longitude columns were selected for in both the MBTA bus and MBTA train datasets. The data were then aggregated into a single dataset containing the locations of all of the aggregated stops.

4. A new dataset containing all of the public schools and colleges was created to include all of the latitude and longitudes of all Boston public schools and colleges. First, the latitude and longitude columns were selected for in both the public schools and colleges datasets. The data were then aggregated into a single dataset containing the locations of all of the aggregated schools.



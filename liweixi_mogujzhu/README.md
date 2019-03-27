# Project Description
In this project, we are collecting data from multiple sources which is need for 
THE ANALYZE BOSTON OPEN DATA CHALLENGE:
https://data.boston.gov/pages/opendatachallenge<br>
We are focus on the Problem Track 4, which is Identifying Fire Risks. <br>
In the project, we collected the data of Boston fire alarm boxes, fire department and fire hydrants.
We did a transformation to map the three datast into one dataset which can
reflect the overall fire facilities condition of Boston.
We also collect the data of History of Boston Fire Incident from 2017-01-01 to 2018-10-31. 
And corresponding Boston Weather condition. We did a transformation to aggregate the daily weather and
 number of incidents to see if they have certain relations.<br>
Finally, we collected the data of Building and Property Violations in Boston to see if such violations can
largely improve the risks of fire incidents. 

# Dataset
* Boston Fire Incident
https://data.boston.gov/dataset/fire-incident-reporting
* Boston Code Enforcement - Building and Property Violations:
https://data.boston.gov/dataset/code-enforcement-building-and-property-violations
* Boston Fire Alarm Boxes
http://bostonopendata-boston.opendata.arcgis.com/datasets/fire-alarm-boxes
* Boston Fire Department
http://bostonopendata-boston.opendata.arcgis.com/datasets/fire-departments
* Boston Fire Hydrants
http://bostonopendata-boston.opendata.arcgis.com/datasets/fire-hydrants
* Boston Weather
https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USW00014739/detail

# Package Dependency
* Pandas: Provide interface to load the data.
  ```
    pip install pandas
  ```
* Numpy: Provide interface to calculate on the data.
  ```
    pip install numpy
  ```
# Data Document
## boston_fire_facility_transformation.py
* facility_type: The type of the facility.<br>
One of [fire_alarm_boxes, fire_hydrants, fire_department]
* coordinates: Coordinates of the facility. <br>
Shape: [latitude, longitude]

## weather_fire_incident_transformation.py
* DATE: The date
* TMAX: The maximum temperature
* TMIN: The minimum temperature
* TAVG: The average temperature
* AWND: Average daily wind speed
* PRCP: Precipitation
* SNOW: Snowfall
* SNWD: Snow depth
* NINCIDENT: Number of fire incident happened
* NLOSS: Number of fire incident which causes money loss

## fire_building_transformation.py
* Street Name: The name of the street which happens fire incident or building violation
* Fire Incident Number: The number of fire incidents that happen on a street
* Building Violation Number: The number of building violations that happen on a street
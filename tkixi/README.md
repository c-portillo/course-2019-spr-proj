# Project 1 
### Gijung(Tony) Kim : tkixi@bu.edu

## Narrative
Tony has always preferred to ride bikes as his commute to class or to work.

As a biker, Tony would like to know what are some of the factors that may contribute to bike accidents. Especially in a city like Boston, it is critical to analyze data on bikes, the weather, traffic signal locations, hubway bike system, and on bike lanes.

Using the following 5 datasets, I computed complex transformations to produce 3 new datasets that would allow bikers to see their own safety in a new light.



## Datasets Used
Data Set|Description
-|-
Boston Hubway Station Location | A dataset provided by Hubway that shows all locations for Hubway bike stations in Boston.
Boston Collisions | A dataset provided by the team of the Vision Zero Boston program that contain the date, time, location, and type of incident
Boston Weather | A dataset provided by NOAA's National Centers for Environmental Information that shows the weather containing information such as precipitation, wind speed, and the date.
Boston Traffic Signal Locations | A dataset provided by the city of Boston's Analyze Boston that contains information on all of Boston's traffic signals
Boston Bike Lanes | A dataset provided by BostonGIS that contains information such as the jurisdiction, street, and the length of the bike lane
---

## Required libraries
```
pip install opencage
```

## Formatting the `auth.json` file

I use OpenCage's reverse geocoder in my transformations so you will need to adjust your auth.json file accordingly.
Here is the link to OpenCage https://opencagedata.com/ 
You should be able to test my transformation with the free version as I have set a bound.
```
{   
    "services": {
        "openCagePortal": {
            "service": "https://opencagedata.com",
            "api_key": "somekey"
        }
    }
}
```


## Running the execution script

```python
python execute.py tkixi
```

## Transformations

transformation1.py : The first transformation takes in the bike lane network and the location of the Hubway station and reverse geocode’s the latitude and longitude of the Hubway station data in order to cross reference the street of the bike lanes and ultimately produce whether or not each bike lane has a Hubway station on its street.

transformation2.py : The second transformation takes in the locations of the traffic signals and the Boston collision datasets and then aggregates every bike collision at a particular intersection, which would help further analyze if the intersection is biker-friendly. 

transformation3.py : The third transformation takes in the data of Boston weather and of the Boston collisions and cross references the city of weather and the collision by reverse geocoding the latitude and longitude of the collision. Then we take in the wind speed on a day that a bike collision occurs and aggregate the average wind speed on a monthly basis of all bike collisions that occurred on a particular month.

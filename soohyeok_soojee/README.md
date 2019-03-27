# CS504 Project#1: Proper Boston Tour

## Contributors:
- Soojee Kim
- Soohyeok Lee

### Project Goal:
Our goal is to determine best travel experiences for incoming tourists within Greater Boston Area. Having such an immense area, people may not have their best experiences in their limited time of travel and we wanted to suggest specific areas based on various datasets for the best possible experience.

### Data sources Used:
- Analyze Boston (*data.boston.gov*)
- Boston Maps Open Data (*bostonopendata-boston.opendata.arcgis.com*)
- Massachusetts Department of Transportation (*geo-massdot.opendata.arcgis.com*)

### Datasets Used:
1. Boston Neighborhoods (*get_neighborhoods.py*)  
https://data.boston.gov/dataset/boston-neighborhoods
2. Crime rate (*get_crimeData.py*)  
https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system
3. Boston Landmarks Commission (BLC) Historic Districts (*get_landmarks.py*)   
http://bostonopendata-boston.opendata.arcgis.com/datasets/547a3ccb7ab443ceaaba62eef6694e74_4
4. MBTA Bus Stops (*get_busStops.py*)  
https://geo-massdot.opendata.arcgis.com/datasets/2c00111621954fa08ff44283364bba70_0
5. MBTA Station stops (*get_trainStations.py*)  
https://geo-massdot.opendata.arcgis.com/datasets/train-stations?geometry=-73.51%2C41.878%2C-69.555%2C42.59

### Project Description:
We currently put together the few datasets listed above and transformed the acquired datasets to see which neighborhoods within the Greater Boston Area  
- has greater number of landmarks to see
- has better system of public transportation
- has low crime rates.

Although we have different datasets of polygons and points, our current project model is heavily dependent on geolocation datsets. We are currently researching on possible datasets to incorporate into our project to further develop user experience.

### Transformation:  
#### *landmarkRate.py*:
- Pulls dataset of polygons from *get_neighborhoods.py*
- Pulls dataset of polygons from *get_landmarks.py*
- Polygon datset of landmarks is averaged into points
- Now that we have points, checks and counts where the crime points are marked within the neighborhood polygons.

#### *crimeRate.py*:
- Pulls dataset of polygons from *get_neighborhoods.py*
- Pulls dataset of points from *get_crimeData.py*
- Checks and counts where the crime occurred within which polygons of neighborhoods.

#### *transportation.py*:
- Pulls dataset of polygons from *get_neighborhoods.py*
- Pulls dataset of points from *get_trainStations.py*
- Pulls dataset of points from *get_busStops.py*
- Merges two dataset of points of bus and train
- Checks and counts where the bus stops and trainstations are within which polygons of neighborhoods.


### Execution Script for Provenance.html:
To execute all the algorithms for the project in an order that respects their explicitly specified data flow dependencies, run the following from the root directory:
```
python execute.py soohyeok_soojee
```

### Note:
If you have any suggestions to improve tourist experience or possible dataset to incorporate onto our project please leave a comment on github or send any of us an e-mail
- soohyeok@bu.edu
- soojee@bu.edu

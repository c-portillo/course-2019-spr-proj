Kerin Grewal and Stephanie Shin 


INSTRUCTIONS: 
Run execute.py to run all data collection, transformations, and provenances, 
by running python3.7 execute.py kgrewal_shin2 in the root project folder. 

 
DATASETS USED: 
1. Boston Street Names 
This data was collected from last semester's project as a CSV and uploaded to datamechanics.io as a .json file. It is a list of all the street names, their genders, and their zipcodes.
This is the base of our information (all of the street names in Boston). 

2. Landmarks 
This data was collected from Boston Landmarks Commission (BLC) Landmarks- http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3. 
This gives us names of landmarks as well as their locations and neighborhoods. 

3. Neighborhoods 
This data was collected from https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/boston.geojson. 
It includes the geographic boundaries of each neighborhood in Boston. 

4. Public Schools 
This data was collected from https://data.boston.gov/dataset/public-schools/resource/6c48e501-3dba-44f3-912f-8a5f309d5df4. 
It includes the locations of public schools in Boston. 

5. Uber data 
This data was collected from Uber including all the information of Uber rides originating at the Boston Common. 
It includes where they ended their Uber rides and the mean time to get there. 

TRANSFORMATIONS: 
transformation1.py - finds the difference between street names, and streets with landmarks on them, selecting only those that are not female street names
transformation2.py - finds streets with no schools at them that are only male or unknown street names 
transformation3.py - finds the number of ubers going to each neighborhood from the Boston Common

FILES: 
in /cleaning: 
street_name_cleaning.py - ran once in order to create json
uber_data_cleaning.py - ran once in order to create json 
test.py - test file for our use previously 
transformations.py - transformation functions as outlined in class 
major_roads_cleaning.py - unused currently, major_roads json file too large to include in project currently









# course-2019-spr-proj README
This project is finished by Chengyu Deng(U68004039, cdeng@bu.edu). There are no other collaborators. 

## General Introduction of the Project
The main object for this course that I would like to achieve is to use data to find the optimal solutions of bikes and bike stations allocation in the Boston area. In this project, the plan is to use the bike sharing datasets to find out some of the most popular bike-sharing stations in Boston and Cambridge areas. Also, I wonder how many bike sharing stations are close to the road where bike lanes are available. 

## The Datasets
I provided 5 datasets for project 1 which are: 
- **Hubway_Stations_as_of_July_2017.csv**
This dataset indicates the total bike sharing locations mainly in Boston and Cambridge areas (some locations are in Somerville and Brookline). It contains important information such as the number of docks at that station, Latitude/Longitude data, street name etc. 
- **201801_hubway_tripdata.csv**
This dataset maintains all the bike trip information in January 2018. It contains data such as trip length, start/end station, and its street name, user type, user gender etc. 
- **201802_hubway_tripdata.csv**
This dataset contains all the bike trip information in February 2018. It has the same schema as the previous dataset. 
- **Existing_Bike_Network.csv**
This dataset is found in Analyze Boston website. It contains all the bike lanes in Boston are.
- **RECREATION_BikeFacilities.csv**
This dataset is found in Geographic Information System in Cambridge City website. It also contains the bike lanes information in the Cambridge area. Notice that the schema of this dataset is different from the Boston bike lane dataset.

These datasets can help to solve my initial questions about bike sharing. Since we have all the station location data and trip data. We can accumulate the trip number for each of the stations to record the popularity of the station. Also, we can use the street name of the bike lane to match the bike station's street name. Hence our initial questions can be solved. In addition, the datasets contain the number of docks in each station. Knowing the trip frequency in a period, we can structure a model to solve the allocation problem in the future project. 

## MongoDB implementation and provenance
I followed the instruction of this project to load the MongoDB in my computer and did the initialization of the environment. Then I created two python files in the cdeng sub-folder. The first file is called **Load_data.py**. It loads all five datasets to the MongoDB and at the same time keep track of the provenance. The second file is called the **Find_popular_stations.py**. This file use relation building blocks to find the most popular station for the incoming trip (first transformation) and the most popular station for the outcoming trip (second transformation) and finally the bike stations close to the bike lane street. I mainly used MongoDB aggregate and a projection method to solve those questions. Also, the provenance for these calculation processes is recorded. 

## How to run the project code
Follow the project 1 instruction to set up the MongoDB environment and run the provided code such as **reset.js** and **setup.js**. Then run the following terminal code:
```javascript
python execute.py cdeng
```
The result will be shown in the terminal and the calculated answers for the questions are stored in the MongoDB. The provenance HTML file will be also created. If there is any question, don't hesitate to contact me. 





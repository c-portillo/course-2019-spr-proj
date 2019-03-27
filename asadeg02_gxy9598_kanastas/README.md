# Project Description And Ideas 

The Main project we are assigned is a spark project named "South Boston Neighborhood Development" the goal of which is to identify buildings that may not even be on the market yet and then finding contact information of the person/people who own it and permit number of the buildings. Since the initial project doesn't meet the requiemetns for project#1 we decided to define some interesting questions whithin the scope of our main project which could be potentially answered using the datasets given to us by spark. Answring these questions and analysing their answers could also provide a solution for the main project. 

The two quesotions to be answred are the following:

1- Finding information about the buildings/properties in the most dangereous neighborhood of Boston area. These infomation include the value of these porpeties, type of the crimes happening in the neighbourhood, perimit number of buildings, owners of the porpeties,...

2- Clustering food stablishments in Boston area using their location and then finding infomation about properties in the most compact cluster (with the most food stablishments in it) to see if access to food stablishments has any impact in the population living in that area or on the value of properties.

---
Data Sets
---

Permit Database : https://data.boston.gov/api/3/action/datastore_search?resource_id=6ddcd912-32a0-43df-9908-63574f8c7e77&limit=125650

Crime Incident Database : https://data.boston.gov/api/3/action/datastore_search?resource_id=12cb3883-56f5-47de-afa5-3b1cf61b257b&limit=366640

Active Food Stablishments: https://data.boston.gov/api/3/action/datastore_search?resource_id=f1e13724-284d-478c-b8bc-ef042aa5b70b&limit=3010

Street Names: https://data.boston.gov/api/3/action/datastore_search?resource_id=a07cc1c6-aa78-4eb3-a005-dcf7a949249f&limit=18992

---
Aditional Resources
---

Zillow Search API: "https://www.zillow.com/howto/api/GetSearchResults.htm"

We are using these API to create a database of the property addresses that are on the market which we are not using for project#1 but is requiered for the main South Boston Neighborhood Development project. 

Accsesssors (Accessing online - City Of Boston): https://www.cityofboston.gov/assessing/search/ 

We are scraping this wesite to find the infomation we are intested in about the propeties in City Of Boston including the value of propeties. This resource is useful for both project#1 and Main project.

**Please note that scraping a website or calling an API is such a slow process and scraping accessors for all the street addresses is boyond the time and resources available so we have put a limit on the number of addresses we want to scrape accsessors for or call the api for**

## Overview Of Transformations 

"aggregateCrimesIncident", "mergeValueWithCrimeRate" and "mergeValueWithPermitAndCrime" are 3 transfomations done to provide an answer for the first question by first aggregating crime incident data set using the "street" attribute as keys and then sorting the result in ascending order then finding the value and ParcelID for the result by scraping `Accsesssors` (we can look at this part of tranfomation as a merge but one of the data sets is in the cloud and not stored in the data base due to time constraints explained) and finally merging the result with crime indincet and permit databases and projecting the desired attributes. Please note that our notion of "the most dangerous" here is the street addresses with the most records in "crime incident report" database.

"foodStablishmentClusters" provides an answer for the second question asked by fisrt clustering food stablishments by ther locations, then counting the number of food stablishments in each cluster, then finding the closest food stablishment center for each building in permit data base) and finally storing the infomation about propeties in the most compact cluster (with the most food stablishments) into a databse.


## Running The Code

In Order to be able to run the code you need to install `selenium` and `xmltodict`. We are using selenium for scraping Accsesssors and using xmltodic for parsing the Zillow Search API responses since they are in xml foramt.

For scraping Accsesssors in scrapeBostonGov method in "mergeValueWithCrimeRate.py" module, you need to specify the path to your chrome web driver. The path already used, is the default path when you install chrome web driver. 
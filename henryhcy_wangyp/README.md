# Project 1: Data Retrieval, Storage, Provenance, and Transformations

### Author 

1. Yuanpei Wang(wangyp@Bu.edu)
2. Chengyang He(henryhcy_wangyp@bu.edu)

### Purpose

The project tries to get the locations of different types of grocery stores such as whole foods market, trader joe's and restaurants. By computing the accessibility to the food resource of individual residents in each neighborhood, we want to analyze whether there is any relationship between the accessibility to the different types of food resources and average income of the neighborhood to check whether there is bias towards food distributions.  

### Database

1. Boston house_hold income (summarized by neighborhood)

   http://datamechanics.io/data/henryhcy_wangyp/household_income.json 

2. Boston poverty_rate (summarized by neighborhood)

   http://datamechanics.io/data/henryhcy_wangyp/poverty_rates.json

3. Boston supermarket or grocerty store

   Using google API

4. Boston active food establishment

   https://data.boston.gov/dataset/active-food-establishment-licenses

5. Boston food establishment-insepctions

   https://data.boston.gov/dataset/food-establishment-inspection

6. Boston neighborhood (get the boundary information of the neighborhood) 

   https://data.boston.gov/dataset/boston-neighborhoods/resource/61988228-017f-46e2-ad0c-ff602362b464

### Data Transformation

1. For the supermarket dataset, since we use google api to retrieve data from google map, the number of dataset we can get is limited. Thus, We called the api many times with different locations. The result dataset will contain a lot of duplicate. We filter out the duplicate and make sure each data has it unique id.
2. We merge the income and poverty dataset, such that each neighborhood will have income and poverty information
3. For the restaurant and inspection dataset, for each data(unique restaurant) in the restaurant data, we find the set of data in the inspection dataset with the same 'property_id' and add the violation level information to the restaurant dataset.

### Result Dataset

RestaurantInspection

IncomeProperty

supermarket

neighborhoods



### 










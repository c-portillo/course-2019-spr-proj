# Taking Gender Equity to the Streets
> Maoxuan Zhu, Dongyi He, Wei Jiang, Kaikang Zhu

This is a Spark! project. Representation is one of MOWA's priority areas. We recognize that male names and pronouns are often the default and given Boston's long parochial history, we want to make sure our City represents its current demographics (52% women). That said, we'd also like to know if there are streets that are good candidates for re-naming (repetitive, etc.).

The goal is to have an interactive site that allows the city and the public to evaluate the different options for renaming based on the different variables provided.  
Most of the needed sets already exist, just need to be analyzed.

## Project #1
In this part we retrived some datasets and managed to transform them into some meaningful datasets using relational primitives.

### Street Book
After our contacts with BU Spark! staff, we get this Street Book dataset which mainly describes basic information of `Street Name`, `Gender`, `Zipcodes`, `Rank`, etc. Therefore, we fully use this dataset with our Famous People one to get related data and generate a new dataset named Filtered_ famous_poeple_streets.

### Famous People
This dataset comes from [https://www.50states.com/bio/mass.htm](https://www.50states.com/bio/mass.htm). We parsed names of famous people and stored them into MongoDB with their `full_name`, `first_name`, `last_name` and `middle_name`.

### UberMovementData
In uber_movement_data.py, we merge two datasets from https://movement.uber.com/?lang=en-US. One of those is uber traffic census data and another one is a json file which store corresponding information of street id and street details. Firstly, we project source positions and aggregate on them. Then we join 2 datasets, select and project to get the final results.

### Colleges and Universities
This dataset comes from [http://bostonopendata-boston.opendata.arcgis.com/datasets/cbf14bb032ef4bd38e20429f71acb61a_2.csv](http://bostonopendata-boston.opendata.arcgis.com/datasets/cbf14bb032ef4bd38e20429f71acb61a_2.csv). For origin dataset, we select and project specific columns(Name, Address, City, Zipcode, Latitude, Longitude) and construct a new dataset named colleges_and_universities. In addition, we store this new dataset in mongodb with the column name mentioned before.

### Public libraries
This dataset can be derived from [http://bostonopendata-boston.opendata.arcgis.com/datasets/cb00f9248aa6404ab741071ca3806c0e_6.csv](http://bostonopendata-boston.opendata.arcgis.com/datasets/cb00f9248aa6404ab741071ca3806c0e_6.csv). For this dataset, we re-arrange the columns and store them into MongoDB with column name `Branch Name`, `Address`, `City`, `Zipcode`, `Latitude`, `Longitude`, `Numbers`.

### Landmarks
This dataset can be derived from [http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.csv](http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.csv). For the origin dataset, we fill in the missing values and select rows that its column "Petiton" > 15. Then project to have a dateset have six cloumns: `Petition`, `Name of landmarks`, `Areas_Desi`, `Address`, `Neighbourhood`, `ShapeSTWidth`. Besides, based on Landmarks dataset and Colleges and Universities dataset, we filter the data and use `City` as the key value to get a new dataset which desrcibes the features related to street names.

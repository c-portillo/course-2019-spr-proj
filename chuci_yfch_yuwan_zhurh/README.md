Description:
For our Unemployment (from lmi2.detma.org and retrieved from datamechanics.io) and 2018 Governor Election dataset (from wbur.org), we did a projection on the Unemployment dataset and only kept the City and the unployment rate��as of Dec 2018��fields. 
We did the same thing on the Governor dataset and kept the Town and the voting percentage for Charlie Baker (2018 MA governor election) fields.
The City and the Town fields are the keys in these two datasets and they have the exact same contents, which is the name of all the towns in Massachusetts. Finally, we join the two datasets together by using the Town field as key and show the unemployment rate and supporting rate for Charlie Baker. 
The resulting dataset can help us to observe the relationship between the unemployment rate and supporting rate for a Republican governor. Therefore, political analysts will be able to use this dataset to understand which party did unemployed people really support.

For the Spark Governor dataset, we collected data from PD43 and created this dataset in order to satifised the requirnment of our Spark partner. This dataset contains all the governor candidates from the elections during 2002-2018.We uploaded this file to datamechanics.io and retrieved it. For this dataset, we did a projection to only keep the Party field and did a aggregate to count the total number of candidates of each party. The result shows that the Republican and Democrat Party both have an overwhelming number of candidates while the Libertarian and Green-Rainbow Party had a fewer number of candidates. This result can be viewed as a microcosm of the political power distribution in Massachusetts.

For the Health and Uber dataset, first of all,at the health_uber_input.py, we retrieve the health dataset from http://datamechanics.io/ and uber dataset from github, these can be counted as from 2 different data portals. After retrieving the data online, we store them to mongodb collection chuci_yfch_yuwan_zhurh.uber and chuci_yfch_yuwan_zhurh.health separatly. Then in the health_uber_output.py, we firstly aggregate chuci_yfch_yuwan_zhurh.health, use CityName as the key and find each CityName's max population, secondly we aggregate chuci_yfch_yuwan_zhurh.uber, use CITY as the key and find each CITY's mean travel time.Finally, we join two dataset together to see each city's population and mean travel time. Since mongodb don't support traditional join, so I use python to do the join work. We want to figure out if there is a relation between a city's population and mean travel time. Unfortunately, due to the limit of data and city, so far we don't find any obvious relation between them.
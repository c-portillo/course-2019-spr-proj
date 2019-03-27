# Project 1

# Data Pools
* datamechanics.io
* zillowstatic.com
* chelseama.gov

# Datsets
* ChelseaAssessorsDatabase2018.json
* 24a90fa2-d3b1-4857-acc1-fbcae3e2cc91.json
* income-in-the-past-12-months.json
* City_ZriPerSqft_AllHomes.csv
* Metro_Zhvi_Summary_AllHomes.csv
* housing-data.xls

We got our datasets from multiple different sources. Some of the datasets were giving us trouble in regards to having an api to read them, so we decided to download them and upload them to datamechanics.io, where we then read the data. Before we uploaded them to datamechanics.io, we used a script to convert them into the json format. For the datasets that didnt need to be uploaded to datamechanics.io, we used their html link to read them and then used pandas to convert the tabular data to json format. We also found more datasets that were relevant to our project, than were required so we put all of them into our database.  

# Transformations
For each of these datasets, they were in a csv/xls format and our main transformations were to convert them from tabular data to json so that they could be properly inserted into our database.

# Running the Tools
We split up the scripts that we wrote to collect and insert the data into two files, data_scripts.py, and data_scripts1.py. The reasoning behind this was simply for organization and keeping track of who works on which parts. The files can be run independently and will collect the data from their respective sources, perform the transformations, insert the data into our database, and generate the prov models. Our code is heavily based on the example.py file that we were given. To run the code, it is very similar to running the example.py file, as all thats needed is to uncomment the lines at the bottom of both data_script files.   
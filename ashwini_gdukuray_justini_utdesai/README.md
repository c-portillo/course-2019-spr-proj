# CS504 Project

## Contributors
- Justin Ingwersen
- Ashwini Kulkarni
- Umang Desai
- Gahouray Dukuray

### Datasets Used
The datasets we chose will be extremely valuable in order to help our partner learn more about the MBE world. They are as follows:
- MBE certification list from massHousing
- MBE certification list from the Secretary of Commonwealth
- Top companies with minority/women majority ownership
- Valid Zip Codes to highlight target areas
- Minority Business Development Agency firm and employee info

Our portals include:
- datamechanics.io
- cs-people.bu.edu
- mbda.gov/mbedata

 The datasets from massHousing and Secretary of Commonwealth are combined into a master list of MBE certified companies.
 This master list will allow many more transformations of data as well as provide a good place to lookup information 
 about specific businesses as needed. We will use the csv containing the top 25 companies with a minority or women 
 majority ownership to compare against the master list. This will show us what companies are top revenue producers as 
 well as MBE certified. It will also draw the question: why are the other top companies not certified in the first 
 place? In addition, we will be using the dataset from MBDA in order to visualize the number of total MBE firms in
 Massachusetts as well as number of employees working in these MBEs. We can also do a comparison against the rest of the
 United States.
 
 Lastly, we also will use a csv file containing a list of zip codes provided by our partner. These are the zip 
 codes we will focus on when analyzing MBE structure and the patterns of the companies. They represent the Greater 
 Boston Area.
 
 ### Non-Trivial Transformations Done/New Datasets Created
 - Our first major transformation was creating the masterList. This initially is a projection when converting the the
 csv file for the Secretary of Commonwealth dataset and the massHousing dataset to a JSON object to be inserted into
 the mongo database. Then we performed a selection of target zip codes, and finished with a union of them together,
 projecting out unwanted columns.
 - Another transformation was an aggregation. This started with taking the masterList and projecting the industries
 represented by the Description of Services. Then, we use an aggregation algorithm to group industries together and get
 the sum of each, resulting in a new dataset (in the form of a dataframe). This will help us see what industry is most
 common for MBEs.
 - Our final transformation involved the dataset containing the top 25 companies and the master list. To get the top 25
 companies, this involved a projection converting the csv file to JSON and inserted into the mongo database. Then, we 
 take the master list and merge it with this top company dataset performing a union. To first do this, we also had to
 transform the top company dataset and add a new column to represent a unique business ID that our master list uses. Our
 resulting data set contains 2 companies, which tells us they are the only two according to our master list that are MBE
 certified.
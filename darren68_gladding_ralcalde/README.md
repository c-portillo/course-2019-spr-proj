Project 1 for team composed by:

Roberto Alcalde Diego,
Darren Hoffmann-Marks,
Alyssa Gladding




For Project 1, we plan at looking at the following five datasets:

1. Revere2014updated.csv
	- This is car accident data for the city of Revere in 2014. Sourced from our Spark Project partner, who originally got it from massDot.
2. Revere2015updated.csv
	- This is car accident data for the city of Revere in 2015. Sourced from our Spark Project partner, who originally got it from massDot.
3. Revere2016updated.csv
	- This is car accident data for the city of Revere in 2016. Sourced from our Spark Project partner, who originally got it from massDot.
4. TotalCrashesbyTownandYear1990_2016updated.csv
	- The is data showing the accidents recorded per year in the cities of Massachussets. Sourced from our Spark Project partner, who
	originally got it from the Registry of Motor Vehicles
5. popData.csv
	- Population data of Suffolk County from 2005 to 2018. Sourced from IPUMS.org(Census Bureau)



The question we want to answer is: Can we identify any way to reduce the amount of car accidents per year in the 
city of Revere?

We plan to combine these data sets to look at a number of things. One of those things is to analyze accident hotspots within Revere. We can look at the manners of collision at those hotspots to see if there is any thing that can be done to reduce the frequency of those types collisions. We also want to compare the rates of change in accidents per year with cities near Revere. If there is a noticeable difference in rates of change of accidents between Revere and another city, it can possibly lead to new questions to ask regarding why there is such a difference. We also plan to use the population data of Suffolk county to determine the 
correlation between population and accidents per year. In the future we also want to look at changes in speed limit on certain roads to see if those changes led to an increase/decrease in accidents per year at certain hotspots.


For this first project, there are three data transformations we performed:

1.  To create our first data set (RevereHotspots) we performed a union on Revere2014updated.csv, Revere2015updated.csv, and    
    Revere2015updated.csv.Then a projection to grab the x,y coordinates and manner of collision for each accident. 
    We dropped the decimals from the x,y coordinates and concatenated the x,y coordinates in a way that allowed
    us to use it as a key for a hotspot. We then performed an aggregation on that returned data. This aggregation
    took all the manners of collision recorded at a hotspot as values and returned a document of the form:

	 {"xycoordinate" : "239612, 909037", "Rear-end" : 11, "Single vehicle crash" : 1, "Angle" : 1, "Sideswipe, same direction" : 1 }

   Which is the x,y coordinate along with the counts associated with each manner of collision. This new data set can 
   allow us to look at the rates of manners of collisions at certain hotspots.

2.  To create our second data set (RoadConditionsEffectRevere2016), we performed a distinct projection on Revere2016.csv data to get the 
    distinct road conditions recorded for accidents. For each distinct road condition, we performed a selection by road condition to     
    project the manners of collision recorded, then combined the returned results to have a data set that had key-value pairs of 
    road conditions with the list of manners of collision recorded with that road condition. We then performed
    an aggregation on the road condition’s associated list to get number of occurrences of each manner of collision.
   
    Here is an example document of the new data set:

	  {"Ice" : { "Angle" : 1, "Single vehicle crash" : 3, "Sideswipe, same direction" : 1, "Sideswipe, opposite direction" : 1, 
     "Rear-end" : 1 }

    This can allow us to determine a correlation between road condition and manner of collision.


3.  The final data set we created (AllTownsRateofChange2010To2016) used the data from TotalCrashesbyTownandYear1990_2016updated.csv to   
    look at the rate of change in accidents per year from 2010 to 2016 for cities in Massachusetts. We performed a projection on the data 
    set to grab the town name, accidents recorded in 2010, and accidents recorded in 2016 to calculate the rate of change. We
    then inserted the rate of change along with the average rate of change into each new document. 

    Here is an example document in the new data set:

	  {
	   "_id" : ObjectId("5c830dade231d7cd19daef34"),
	   "Town" : "ABINGTON",
	   "2010" : "390",
	   "2016" : "447",
	   "% Change 2010-2016" : "14.61%",
	   "Average % Change 2010-2016" : "61.10%"
	   }
     
     This data set will allow us to use population data along with data showing use of ride-sharing apps to see if there is a
     correlation between the rise of ride-sharing apps and frequency of accidents.

requirements:
decorator==4.3.2
dml==0.0.16.0
isodate==0.6.0
lxml==4.3.2
networkx==2.2
protoql==0.0.3.0
prov==1.5.3
pymongo==3.7.2
pyparsing==2.3.1
python-dateutil==2.8.0
rdflib==4.2.2
six==1.12.0







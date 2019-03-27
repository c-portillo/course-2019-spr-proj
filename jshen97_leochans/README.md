<b>The Analysis of Franchising brands in Boston Area</b>

Team formation: <br>
JiajiaShen: jshen97@bu.edu <br>
ShiweiChen: leochans@bu.edu

<b>Project 1 README</b>

<b>(1) General Description:</b>
The project picks two of the most popular franchising retailer brands in Boston: CVS and Walgreen (7Eleven as backup)
to generate/acquire a “target” dataset based on its geographical location. Experiment/Integrate the dataset with other available 
geo-location related “guest” datasets including crimelog boston, streetlight location boston, and evictionIncidents boston to see
if the integration/computation will produce some interesting results.
 
<b>(2) General Methodology:</b>
Presume a relationship between the target dataset and guest datasets (i.e. number of customers per day is inverse proportional to 
crime rate, is proportional to the square of resident income, etc.) then we experiment to see if the hypothesis holds and try to 
explain why or why not.
 
<b>(3) Obtained Datasets and Resources:</b><br>
   a. Cvs stores within 15 km boston area through querying Google Places API (Search Nearby) <br>
   b. Walgreen stores within 15 km boston area through querying Google Places API (Search Nearby) <br>
   c. 7Eleven stores within 15 km boston area through querying Google Places API (Search Nearby) <br>
   d. Streetlight Locations in boston area through querying Boston Data Portal (Analyze Boston) <br>
   e. Eviction Incidents in boston area from http://datamechanics.io/data/evictions_boston.csv <br>
   f. Crime Incidents in boston area from http://datamechanics.io/dadta/crime.csv <br>
   g. MBTA stops in boston area from http://datamechanics.io/data/MBTA_Stops.json <br>
   
<b>(4) Performed Transformations and Incentives:</b><br>
   a. Combined cvs and walgreen into a collection named cvsWalgreen in cvsWalgreen.py This transformation provides us the insight of the geo-distribution of the two competing retailer: CVS and Walgreen. Questions like "How to quantify the competition between CVS and Walgreen?" can be well answered. <br>
   b. Took those eviction incidences that are within 15 km of boston collection then combined them each with cvs collection and walgreen collection in CvsWalEviction.py. Lat/Lng Distance is calculated using Haversine Formula. This transformation can potentially provide us the underlying relationship between Personal Finanial Instability and Retailer Store Locations. Questions like "what is the subtle difference between CVS target customers and walgreen's target customers?" can be well answered. <br>
   c. Retrieve MBTA Stops in MBTAstops.py. This transformation retrieves data from http://datamechanics.io/data/MBTA_Stops for later applications. In the future, we can apply that if in a short distance such as 1 mile, there exists multiple stops, we assume that area has many human traffic, and we can suggest start-up business to locate that specific area. 

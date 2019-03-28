# CS504 Project: Revere Crash Data History

Using Revere traffic collision data from 2002-2018, and combining it with other data sources, we want to find the factors that contribute the most to causing traffic collisions. The factors we want to consider are:
- Weather (daily weather information from NOAA)
- Pedestrians (predicted by population data)
- New Development (shown by City data of recent and anticipated development)
- Speed limits (from the Google Roads API and Waze)
- Flooding and extreme weather (because Revere is on the coast)
- Natural ambient Light (from databases that show time of day and season and natural light at those hours)
- Other Similar Cities (from MassDOT), compare to Lynn, Chelsea, Malden, Medford, Everett, Quincy

We want to use a difference in differences technique to model the factors, including heat-mapping historical accident data and how it has changed over time..

Then, using the Revere traffic collision data, we want to create a predictive heat map to show where traffic collisions are most likely to happen in Revere, given the factors above. We want to do predictive analysis based on where development is happening to determine where future traffic accident hotspots may occur in the future. 


## Group Member
- Zehui Jiang
- Runqi Tian
- Xin He
- Hongyao Fei

### Datasets
- Revere Crash Data 01-19
- Town Varied Crash Data
- Fatality vs Town
- Revere Units Added
- Unit Annual Difference

These datasets contains information about every recorded car crash in Revere in the last 20 years. Along with the detail of every crash like IDs, weather condition, place of crash, fatality, etc.

Source / portals of datasets:
- Revere government
- services.massdot.state.ma.us/crashportal

Datasets may come in as .pdf file, .xlsx file or .txt file. We have convert them all to .csv file or .json file and uploaded to datamechism.io for further use.

### Non-Trivial Transformations Done/New Datasets Created

- Our first major transformation was creating the crash file. We extracted all the parameters that we find relevent to the crash. In this case, we chose Light condition, Weather, Fatality and of course, ID of the crash. This projection will give us more convenience in studying the relationship between natural factors and the occurrance of the crash.

 - Another transformation was an aggregation. This started with taking annual increase in units in different location in Revere. As we ahave no access to the annaully traffic information, the increase in units stands for the traffic of each location. But in this case, we would like to first study the annual change of traffic data. So we aggregate the unit change number by year.

 - Our final transformation involved the dataset containing the crash data in several other towns near Revere. With this dataset, we want a town-oriented study and compare the statistics in Revere to that of other surrounding towns. So we first use a projection to cleanup crash Ids as there may exists two different kind of notation. Then we use another projection to put the ID together with crash date, time and most importantly, in which town.

**The right to use these data is granted**
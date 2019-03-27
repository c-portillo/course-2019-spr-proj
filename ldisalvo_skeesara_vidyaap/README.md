# course-2019-spr-proj
Team Members: Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara

Directory: ldisalvo_skeesara_vidyaap

## Project Justification
The below datasets can be combined to score the ideologies of voting districts within Massachusetts. The election data will help to identify which political party residents in that district typically vote for. The demographic census data can be used to determine predictors of voting patterns within each county and town. We plan to use the county shapes data to build our visualization of voting districts. We also plan to characterize each ballot question ideologically by comparing districts that voted in favor of the ballot question with those that voted for certain party candidates in the same year.  

## Datasets
### ballotQuestions
contains: data about each Massachusetts Ballot Question from 2000 to 2018

source: http://electionstats.state.ma.us/ballot_questions/search/year_from:2000/year_to:2018
```
{
    "_id" : "7322",
    "year" : 2018,
    "number" : "4",
    "description" : "SUMMARY Sections 3 to 7 of Chapter 44B of the General Laws
        of Massachusetts, also known as the Community Preservation Act (the 'Act'),
        establishes a dedicated funding source for the: acquisition, creation and
        preservation of open space; acquisition, preservation, rehabilitation and
        restoration of hi...",
    "type" : "Local Question",
    "location" : "Various cities/towns"
}
```

### ballotQuestionsResults
contains: data about voting results for each Massachusetts Ballot Question from 2000 to 2018

source: http://electionstats.state.ma.us/ballot_questions/download/7303/precincts_include:1/
```
{
    "Locality" : "Bourne",
    "Ward" : "-",
    "Pct" : "7",
    "Yes" : 375,
    "No" : 914,
    "Blanks" : 26,
    "Total Votes Cast" : 1315,
    "Question ID" : "7303"
}
```
### stateHouseElections
contains: data about each Massachusetts General State House Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/search/year_from:2000/year_to:2018/office_id:8/stage:General
```
{
    "_id" : "131672",
    "year" : 2018,
    "district" : "3rd Bristol",
    "candidates" :
    [ {
        "name" : "Shaunna L. O'Connell",
        "party" : "Republican",
        "isWinner" : true
    },
    {
        "name" : "Emily Jm Farrer",
        "party" : "Democratic",
        "isWinner" : false
    } ]
}
```
### stateHouseElectionsResults
contains: data about voting results for each Massachusetts General State House Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/download/131581/precincts_include:1/
```
{
    "City/Town" : "Barnstable",
    "Ward" : "-",
    "Pct" : "7",
    "Election ID" : "131582",
    "William L Crocker, Jr" : 1079,
    "Paul J Cusack" : 1059,
    "All Others" : 5,
    "Blanks" : 42,
    "Total Votes Cast" : 2185
}
```
### stateSenateElections
contains: data about each Massachusetts General State Senate Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/search/year_from:2000/year_to:2018/office_id:9/stage:General
```
{
    "_id" : "131666",
    "year" : 2018,
    "district" : "1st Middlesex",
    "candidates" :
    [ {
        "name" : "Edward J. Kennedy",
        "party" : "Democratic",
        "isWinner" : true
    }, {
        "name" : "John A. Macdonald",
        "party" : "Republican",
        "isWinner" : false
    } ] 
}
```
### stateSenateElectionsResults
contains: data about voting results for each Massachusetts General State Senate Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/download/131526/precincts_include:1/

```
{
    "City/Town" : "Egremont",
    "Ward" : "-",
    "Pct" : "1",
    "Election ID" : "131526",
    "Adam G Hinds" : 682,
    "All Others" : 0,
    "Blanks" : 111,
    "Total Votes Cast" : 793
}
```
### countyShapes
contains: geoJSON data about each Massachusetts county (taken from Google Fusion Table and uploaded to datamechanics.io)

source: http://datamechanics.io/data/massachusetts_counties.csv
```
{
    "_id" : "7322",
    "Name" : Barnstable,
    "Shape" : "<Polygon> ... ",
    "Geo_ID" : "25001",
}
```
### demographicDataCounty
contains: demographic data for Massachusetts by county from census.gov (to see full list of fields, go to https://www.census.gov/quickfacts/fact/table/ma/PST045217)
```
{ "Barnstable County, Massachusetts":
   "Population estimates, July 1, 2017,  (V2017)": "213,444",
   "Population estimates base, April 1, 2010,  (V2017)": "215,868",
   "Population, percent change - April 1, 2010 (estimates base) to July 1, 2017,  (V2017)": "-1.1%",
   "Population, Census, April 1, 2010": "215,888",
   "Persons under 5 years, percent": "3.6%",
   "Persons under 18 years, percent": "15.1%",
   ..........................
}
```

### demographicDataTown
contains: demographic data for Massachusetts by town from census.gov (to see full list of fields, go to https://www.census.gov/quickfacts/fact/table/ma/PST045217)
```
{ "Winchester town, Middlesex County, Massachusetts":
  "Population estimates, July 1, 2017,  (V2017)": "23,339",
  "Population estimates base, April 1, 2010,  (V2017)": "23,797",
  "Population, percent change - April 1, 2010 (estimates base) to July 1, 2017,  (V2017)": "-1.9%",
  "Population, Census, April 1, 2010": "23,793",
  ..........................
}
```

## Transformations
### House District Ideology
Calculates a basic ideology score for each state house electoral district (160) by counting number of Democratic and Republican wins from 2000 to 2018

```
{
    "district" : "1st Barnstable",
    "percentDem" : 25,
    "percentRepub" : 75,
    "numDemWins" : 1,
    "numRepubWins" : 3,
    "numElections" : 4
}
```

### Senate District Ideology
Calculates a basic ideology score for each state senate electoral district (51) by counting number of Democratic and Republican wins from 2000 to 2018

```
{
    "district" : "1st Hampden and Hampshire",
    "percentDem" : 70, 
    "percentRepub" : 30, 
    "numDemWins" : 7,
    "numRepubWins" : 3, 
    "numElections" : 10 
}

```


### Weighted Senate Ideology
Calculates a weighted ideology score for each state senate electoral district by creating a ratio of type of vote to total vote in each year and finding the average

```
{
    "district" : "1st Hampden and Hampshire",
    "Democratic ratio" : .6,
    "Republican ratio" : .2,
    "Others ratio" : .1,
    "Blanks ratios" : .1,
    "Totals" : 1
}

```

### Weighted House Ideology
Calculates a weighted ideology score for each state house electoral district by creating a ratio of type of vote to total vote in each year and finding the average

```
{
    "district" : "1st Hampden and Hampshire",
    "Democratic ratio" : .6,
    "Republican ratio" : .2,
    "Others ratio" : .1,
    "Blanks ratios" : .1,
    "Totals" : 1
}

```

### Demographic Summary Metrics
Retrieves summary demographic data for all facts by county and town. Displays maximum and minimum values and corresponding towns for each fact.
```
{
    'Fact': 'Population estimates, July 1, 2017,  (V2017)',
    'Town_Min': 'Middleton town, Essex County, Massachusetts',
    'Town_Min_Val': '9,861',
    'Town_Max': 'Littleton town, Middlesex County, Massachusetts',
    'Town_Max_Value': '10,115',
    'County_Min': 'Worcester County, Massachusetts',
    'County_Min_Val': '826,116',
    'County_Max': 'Middlesex County, Massachusetts',
    'County_Max_Value': '1,602,947'}
}

```

## Additional Python Libraries
You may need to import the following libraries to access our datasets: bs4, pandas, requests, csv, io

They can be installed by running the requirements.txt file

```
pip3 install requirements.txt
```

If you get a 'SSL: CERTIFICATE_VERIFY_FAILED' error, you need to install certificates for your version of Python. In MacOS, navigate to Finder->Applications->Python3.7 and double click on 'InstallCertificates.command' and then on 'UpdateShellProfile.command'.
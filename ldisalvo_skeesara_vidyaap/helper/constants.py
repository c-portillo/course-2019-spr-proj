"""
CS504 : constants
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

February 28, 2019
"""

# mongodb collection names
TEAM_NAME = "ldisalvo_skeesara_vidyaap"

BALLOT_QUESTIONS = "ballotQuestions"
BALLOT_QUESTIONS_RESULTS = "ballotQuestionsResults"
BALLOT_QUESTIONS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=BALLOT_QUESTIONS)
BALLOT_QUESTIONS_RESULTS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=BALLOT_QUESTIONS_RESULTS)

STATE_HOUSE_ELECTIONS = "stateHouseElections"
STATE_HOUSE_ELECTIONS_RESULTS = "stateHouseElectionsResults"
STATE_HOUSE_ELECTIONS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=STATE_HOUSE_ELECTIONS)
STATE_HOUSE_ELECTIONS_RESULTS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=STATE_HOUSE_ELECTIONS_RESULTS)
HOUSE_DISTRICT_IDEOLOGIES = "houseDistrictIdeologies"
HOUSE_DISTRICT_IDEOLOGIES_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=HOUSE_DISTRICT_IDEOLOGIES)

STATE_SENATE_ELECTIONS = "stateSenateElections"
STATE_SENATE_ELECTIONS_RESULTS = "stateSenateElectionsResults"
STATE_SENATE_ELECTIONS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=STATE_SENATE_ELECTIONS)
STATE_SENATE_ELECTIONS_RESULTS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=STATE_SENATE_ELECTIONS_RESULTS)
SENATE_DISTRICT_IDEOLOGIES = "senateDistrictIdeologies"
SENATE_DISTRICT_IDEOLOGIES_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=SENATE_DISTRICT_IDEOLOGIES)

DEMOGRAPHIC_DATA_COUNTY = "demographicDataCounty"
DEMOGRAPHIC_DATA_COUNTY_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=DEMOGRAPHIC_DATA_COUNTY)

COUNTY_SHAPE = "countyShape"
COUNTY_SHAPE_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=COUNTY_SHAPE)

WEIGHTED_SENATE_IDEOLOGIES = "weightedSenateIdeologies"
WEIGHTED_SENATE_IDEOLOGIES_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=WEIGHTED_SENATE_IDEOLOGIES)

WEIGHTED_HOUSE_IDEOLOGIES = "weightedHouseIdeologies"
WEIGHTED_HOUSE_IDEOLOGIES_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=WEIGHTED_HOUSE_IDEOLOGIES)

DEMOGRAPHIC_DATA_TOWN = "demographicDataTown"
DEMOGRAPHIC_DATA_TOWN_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=DEMOGRAPHIC_DATA_TOWN)


SUMMARY_DEMOGRAPHICS_METRICS = "summaryDemographicsMetrics"
SUMMARY_DEMOGRAPHICS_METRICS_NAME = "ldisalvo_skeesara_vidyaap.{name}".format(name=SUMMARY_DEMOGRAPHICS_METRICS)


# electionstats URLs
BALLOT_QUESTION_2000_2018_URL = "http://electionstats.state.ma.us/ballot_questions/search/year_from:2000/year_to:2018"
STATE_HOUSE_GENERAL_2000_2018_URL = "http://electionstats.state.ma.us/elections/search/year_from:2000/year_to:2018/office_id:8/stage:General"
STATE_SENATE_GENERAL_2000_2018_URL = "http://electionstats.state.ma.us/elections/search/year_from:2000/year_to:2018/office_id:9/stage:General"

BALLOT_QUESTION_DOWNLOAD_RESULTS_URL = "http://electionstats.state.ma.us/ballot_questions/download/{id}/precincts_include:1/"
ELECTION_DOWNLOAD_RESULTS_URL = "http://electionstats.state.ma.us/elections/download/{id}/precincts_include:1/"


# geographic data
MA_COUNTY_LIST = ["Barnstable County", "Berkshire County", "Bristol County", "Dukes County", "Essex County",
                  "Franklin County", "Hampden County", "Hampshire County","Middlesex County", "Nantucket County",
                  "Norfolk County", "Plymouth County", "Suffolk County", "Worcester County"]

MA_TOWN_LIST = ["Adams town, Berkshire County", "Great Barrington town, Berkshire County",
                "Lee town, Berkshire County", "Dalton town, Berkshire County", "Williamstown town, Berkshire County",
                "Abington town, Plymouth County", "Acton town, Middlesex County", "Acushnet town, Bristol County",
                "Amherst town, Hampshire County", "Andover town, Essex County", "Arlington town, Middlesex County",
                "Ashburnham town, Worcester County", "Ashland town, Middlesex County", "Athol town, Worcester County",
                "Auburn town, Worcester County", "Ayer town, Middlesex County", "Barre town, Worcester County",
                "Bedford town, Middlesex County","Belchertown town, Hampshire County", "Bellingham town, Norfolk County",
                "Belmont town, Middlesex County", "Berkley town, Bristol County", "Billerica town, Middlesex County",
                "Blackstone town, Worcester County", "Bolton town, Worcester County", "Bourne town, Barnstable County",
                "Boxborough town, Middlesex County", "Boxford town, Essex County", "Brewster town, Barnstable County",
                "Bridgewater town, Plymouth County", "Brookline town, Norfolk County", "Burlington town, Middlesex County",
                "Canton town, Norfolk County", "Carlisle town, Middlesex County", "Carver town, Plymouth County",
                "Charlton town, Worcester County", "Chatham town, Barnstable County", "Chelmsford town, Middlesex County",
                "Clinton town, Worcester County", "Cohasset town, Norfolk County", "Concord town, Middlesex County",
                "Danvers town, Essex County", "Dartmouth town, Bristol County", "Dedham town, Norfolk County",
                "Deerfield town, Franklin County", "Dennis town, Barnstable County", "Dighton town, Bristol County",
                "Douglas town, Worcester County", "Dover town, Norfolk County", "Dracut town, Middlesex County",
                "Dudley town, Worcester County", "Duxbury town, Plymouth County", "East Bridgewater town, Plymouth County",
                "East Longmeadow town, Hampden County", "Easton town, Bristol County", "Fairhaven town, Bristol County",
                "Falmouth town, Barnstable County", "Foxborough town, Norfolk County", "Framingham town, Middlesex County",
                "Freetown town, Bristol County", "Georgetown town, Essex County", "Grafton town, Worcester County",
                "Granby town, Hampshire County", "Groton town, Middlesex County", "Groveland town, Essex County",
                "Hadley town, Hampshire County", "Halifax town, Plymouth County", "Hamilton town, Essex County",
                "Hampden town, Hampden County", "Hanover town, Plymouth County", "Hanson town, Plymouth County",
                "Harvard town, Worcester County", "Harwich town, Barnstable County", "Hingham town, Plymouth County",
                "Holbrook town, Norfolk County", "Holden town, Worcester County", "Holliston town, Middlesex County",
                "Hopedale town, Worcester County", "Hopkinton town, Middlesex County", "Hudson town, Middlesex County",
                "Hull town, Plymouth County", "Ipswich town, Essex County", "Kingston town, Plymouth County",
                "Lakeville town, Plymouth County", "Lancaster town, Worcester County", "Leicester town, Worcester County",
                "Lexington town, Middlesex County", "Lincoln town, Middlesex County", "Littleton town, Middlesex County",
                "Longmeadow town, Hampden County", "Ludlow town, Hampden County", "Lunenburg town, Worcester County",
                "Lynnfield town, Essex County", "Manchester-by-the-Sea town, Essex County", "Mansfield town, Bristol County",
                "Marblehead town, Essex County", "Marion town, Plymouth County", "Marshfield town, Plymouth County",
                "Mashpee town, Barnstable County", "Mattapoisett town, Plymouth County", "Maynard town, Middlesex County",
                "Medfield town, Norfolk County", "Medway town, Norfolk County", "Mendon town, Worcester County",
                "Merrimac town, Essex County", "Middleborough town, Plymouth County", "Middleton town, Essex County",
                "Milford town, Worcester County", "Millbury town, Worcester County", "Millis town, Norfolk County",
                "Milton town, Norfolk County", "Monson town, Hampden County", "Montague town, Franklin County",
                "Nantucket town, Nantucket County", "Natick town, Middlesex County", "Needham town, Norfolk County",
                "Newbury town, Essex County", "Norfolk town, Norfolk County", "North Andover town, Essex County",
                "North Attleborough town, Bristol County", "North Reading town, Middlesex County",
                "Northborough town, Worcester County", "Northbridge town, Worcester County", "Norton town, Bristol County",
                "Norwell town, Plymouth County", "Norwood town, Norfolk County", "Orange town, Franklin County",
                "Orleans town, Barnstable County", "Oxford town, Worcester County", "Pembroke town, Plymouth County",
                "Pepperell town, Middlesex County", "Plainville town, Norfolk County", "Plymouth town, Plymouth County",
                "Randolph town, Norfolk County", "Raynham town, Bristol County", "Reading town, Middlesex County",
                "Rehoboth town, Bristol County", "Rochester town, Plymouth County", "Rockland town, Plymouth County",
                "Rockport town, Essex County", "Rowley town, Essex County", "Rutland town, Worcester County",
                "Salisbury town, Essex County", "Sandwich town, Barnstable County", "Saugus town, Essex County",
                "Scituate town, Plymouth County", "Seekonk town, Bristol County", "Sharon town, Norfolk County",
                "Shirley town, Middlesex County", "Shrewsbury town, Worcester County", "Somerset town, Bristol County",
                "South Hadley town, Hampshire County", "Southampton town, Hampshire County", "Southborough town, Worcester County",
                "Southwick town, Hampden County", "Spencer town, Worcester County", "Sterling town, Worcester County",
                "Stoneham town, Middlesex County", "Stoughton town, Norfolk County", "Stow town, Middlesex County",
                "Sturbridge town, Worcester County", "Sudbury town, Middlesex County", "Sutton town, Worcester County",
                "Swampscott town, Essex County, Massachusetts", "Swansea town, Bristol County", "Templeton town, Worcester County",
                "Tewksbury town, Middlesex County", "Topsfield town, Essex County", "Townsend town, Middlesex County",
                "Tyngsborough town, Middlesex County", "Upton town, Worcester County", "Uxbridge town, Worcester County",
                "Wakefield town, Middlesex County", "Walpole town, Norfolk County", "Ware town, Hampshire County",
                "Wareham town, Plymouth County", "Warren town, Worcester County", "Wayland town, Middlesex County",
                "Webster town, Worcester County", "Wellesley town, Norfolk County", "Wenham town, Essex County",
                "West Boylston town, Worcester County", "West Bridgewater town, Plymouth County",
                "Westborough town, Worcester County", "Westford town, Middlesex County", "Westminster town, Worcester County",
                "Weston town, Middlesex County", "Westport town, Bristol County", "Westwood town, Norfolk County",
                "Whitman town, Plymouth County", "Wilbraham town, Hampden County", "Wilmington town, Middlesex County",
                "Winchendon town, Worcester County", "Winchester town, Middlesex County", "Wrentham town, Norfolk County",
                "Yarmouth town, Barnstable County"]

# census.gov URLs (TODO: merge URLs)
COUNTY_URL = "https://www.census.gov/quickfacts/fact/csv//PST045218"
TOWN_URL = "https://www.census.gov/quickfacts/fact/csv//PST045218"

#county shape data
FUSION_TABLE_URL = "http://datamechanics.io/data/ldisalvo_skeesara_vidyaap/massachusetts_counties.csv"
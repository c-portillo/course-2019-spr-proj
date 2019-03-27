import urllib.request
import csv
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

'''
Goal: Combine datasets containing information about crime and police stations in Boston
Purpose: Match crime rates to neighborhoods
'''


# Helper Functions
def project(R, p):
    return [p(t) for t in R]


def select(R, s):
    return [t for t in R if s(t)]


def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k, v) in R if k == key])) for key in keys]


# transformation
class crimeLoc(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = ['kzhang21_ryuc.crime', 'kzhang21_ryuc.station']
    writes = ['kzhang21_ryuc.crimeLoc']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        # retrieve data sets
        crimeData = pd.DataFrame(repo.kzhang21_ryuc.crime.find())
        stationData = pd.DataFrame(repo.kzhang21_ryuc.station.find())

        '''Prepare Crime Data'''
        # clean data and organize into keys
        tempC = crimeData.to_numpy()
        tempC = project(tempC[1:], lambda c: ((c[0], c[1], c[3]), 1))
        # aggregate and get total of crime a month for each year in each neighborhood
        tempC = aggregate(tempC, sum)
        #                                     district    year      month        # crimes
        tempC = project(tempC, lambda dyms:(dyms[0][0], dyms[0][1], dyms[0][2], dyms[1]))

        '''Prepare Station Data'''
        # clean station data
        tempS = stationData.to_numpy()
        tempS = select(tempS, lambda dnz: dnz[0][0:8] == 'District')
        tempS = project(tempS, lambda s: (s[0][9] + s[0][11:-15], s[1], s[2]))

        # make dictionary from stations
        zip = {}
        neigh = {}
        for row in tempS:
            key = row[0]
            if key not in zip:
                zip[key] = row[2]
                neigh[key] = row[1]

        # back to pandas
        result = pd.DataFrame(data=tempC)
        result.columns = ['District', 'Month', 'Year', 'Crime']

        result['Zip'] = result['District'].map(zip,na_action='ignore')
        result['Neighborhood'] = result['District'].map(neigh,na_action='ignore')
        col = ['Neighborhood','Zip','Year','Month','District','Crime']
        result = result[col]
        result.dropna(inplace=True)

        # sort by neighborhood
        result.sort_values(by=['Neighborhood'], inplace = True)

        print(result[0:10])

        # print(result[0:10])
        r = json.loads(result.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("crimeLoc")
        repo.createCollection("crimeLoc")
        repo['kzhang21_ryuc.crimeLoc'].insert_many(r)
        repo['kzhang21_ryuc.crimeLoc'].metadata({'complete': True})
        print(repo['kzhang21_ryuc.crimeLoc'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        # additional resource
        doc.add_namespace('crime',
                          'https://data.boston.gov/dataset/6220d948-eae2-4e4b-8723-2dc8e67722a3/resource/12cb3883-56f5-47de-afa5-3b1cf61b257b/download/tmpxjqz5gin.csv')
        doc.add_namespace('station',
                          'http://bostonopendata-boston.opendata.arcgis.com/datasets/e5a0066d38ac4e2abbc7918197a4f6af_6.csv')

        this_script = doc.agent('alg:kzhang21_ryuc#crimeLoc',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:kzhang21_ryuc#crime',
                              {'prov:label': 'Crime and Station Search', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_lit = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_lit, this_script)
        doc.usage(get_lit, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'
                   }
                  )

        crimeLoc = doc.entity('dat:kzhang21_ryuc#crimeLoc',
                              {prov.model.PROV_LABEL: 'Crime and Station Matching',
                               prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crimeLoc, this_script)
        doc.wasGeneratedBy(crimeLoc, get_lit, endTime)
        doc.wasDerivedFrom(crimeLoc, resource, get_lit, get_lit, get_lit)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# crimeLoc.execute()
# doc = crimeLoc.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof

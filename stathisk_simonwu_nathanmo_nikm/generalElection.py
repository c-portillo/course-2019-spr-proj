import urllib.request
import dml
import prov.model
import datetime
import uuid
from io import StringIO
import pandas as pd

class transformGeneral(dml.Algorithm):
    contributor = 'stathisk_simonwu_nathanmo_nikm'
    reads = []
    writes = ['stathisk_simonwu_nathanmo_nikm.aggGeneralData']

    @staticmethod
    def projectGeneral(df):
        """Takes pandas df for general election and removes Pct and Ward"""
        df = df.drop(['Ward', 'Pct'], axis=1)
        df = df.drop([0])
        return df

    @staticmethod
    def removePeriods(d):
        """Takes a dictionary and removes periods from the keys"""
        for key in d:
            if '.' in key:
                newKey = key.replace('.', '')
                d[newKey] = d[key]
                del d[key]
        return d


    @staticmethod
    def getAggByTownResponse(response):
        """Sum of votes for each candidate for each town
        same as previous function just modified for URL response"""
        # Aggregate by city, ward, and psc
        # lol = getData(filename)
        data = StringIO(response)
        df = pd.read_csv(data)
        df = transformGeneral.projectGeneral(df)
        lol = df.values.tolist()
        # Extra projection to remove row number
        lol = [row[1:] for row in lol]

        # aggSum for each category in each town
        d = {}
        for row in lol:
            if row[0] not in d:
                toInsert = row[1:]
                # change string values to ints
                toInsert = [s.replace(',', '') for s in toInsert if type(s) != float]
                toInsert = [int(num) for num in toInsert]
                d[row[0]] = toInsert
            else:
                # town is already accounted for and need to increment values
                toInsert = row[1:]
                toInsert = [s.replace(',', '') for s in toInsert if type(s) != float]
                toInsert = [int(num) for num in toInsert]
                for i in range(len(d[row[0]])):
                    d[row[0]][i] += toInsert[i]
        return d

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')

        # url = 'http://cs-people.bu.edu/lapets/591/examples/lost.json'
        url = 'http://datamechanics.io/data/generalElectionData.csv'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        transformedData = transformGeneral.removePeriods(transformGeneral.getAggByTownResponse(response))
        # repo.dropCollection("lost")
        repo.createCollection("stathisk_simonwu_nathanmo_nikm.aggGeneralData")
        #need to remove periods

        repo['stathisk_simonwu_nathanmo_nikm.aggGeneralData'].insert(transformedData)
        repo['stathisk_simonwu_nathanmo_nikm.aggGeneralData'].metadata({'complete': True})
        print(repo['stathisk_simonwu_nathanmo_nikm.aggGeneralData'].metadata())

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
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:stathisk_simonwu_nathanmo_nikm#transformGeneral',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('dat:generalElectionData',
                              {'prov:label': 'Information on general election', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_general = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_general, this_script)

        doc.usage(get_general, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:DataResource'})
        # change 'avg' title to 'agg' above later
        aggByTown = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#aggGeneralData',
                                                    {prov.model.PROV_LABEL: 'general election votes by county',
                                                     prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(aggByTown, this_script)
        doc.wasDerivedFrom(aggByTown, resource, get_general, get_general, get_general)
        doc.wasGeneratedBy(aggByTown, resource, endTime)


        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
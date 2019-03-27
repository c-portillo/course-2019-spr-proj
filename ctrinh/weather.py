import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class weather(dml.Algorithm):
    contributor = 'ctrinh'
    reads = []
    writes = ['ctrinh.weather']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ctrinh', 'ctrinh')

        # Weather dataset from 2018.
        url1 = 'http://datamechanics.io/data/weather-2018.csv'
        df1 = pd.read_csv(url1)

        df = df1.filter(['DATE', 'MonthlyMaximumTemperature', 'MonthlyMeanTemperature', 'MonthlyMinimumTemperature', 'MonthlyTotalLiquidPrecipitation', 'MonthlyTotalSnowfall'])
        r = df.to_dict(orient='records')

        repo.dropCollection("weather18")
        repo.createCollection("weather18")
        repo['ctrinh.weather18'].insert_many(r)
        repo['ctrinh.weather18'].metadata({'complete':True})
        print(repo['ctrinh.weather18'].metadata())

        # Weather dataset from 2015.
        url2 = 'http://datamechanics.io/data/weather-2015.csv'
        df2 = pd.read_csv(url2)

        df = df2.filter(['DATE', 'MonthlyMaximumTemperature', 'MonthlyMeanTemperature', 'MonthlyMinimumTemperature', 'MonthlyTotalLiquidPrecipitation', 'MonthlyTotalSnowfall'])
        r = df.to_dict(orient='records')

        repo.dropCollection("weather15")
        repo.createCollection("weather15")
        repo['ctrinh.weather15'].insert_many(r)
        repo['ctrinh.weather15'].metadata({'complete':True})
        print(repo['ctrinh.weather15'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ctrinh', 'ctrinh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('dmc', 'http://datamechanics.io/data/')

        this_script = doc.agent('alg:ctrinh#weather', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dmc:weather-$.csv', {'prov:label':'Monthly Climate Report', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_weather18 = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_weather15 = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_weather18, this_script)
        doc.wasAssociatedWith(get_weather15, this_script)
        doc.usage(get_weather18, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'}
                  )
        doc.usage(get_weather15, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'}
                  )

        weather18 = doc.entity('dat:ctrinh#weather18', {prov.model.PROV_LABEL:'Weather 2018', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(weather18, this_script)
        doc.wasGeneratedBy(weather18, get_weather18, endTime)
        doc.wasDerivedFrom(weather18, resource, get_weather18, get_weather18, get_weather18)

        weather15 = doc.entity('dat:ctrinh#weather15', {prov.model.PROV_LABEL:'Weather 2015', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(weather15, this_script)
        doc.wasGeneratedBy(weather15, get_weather15, endTime)
        doc.wasDerivedFrom(weather15, resource, get_weather15, get_weather15, get_weather15)



        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
weather.execute()
doc = weather.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

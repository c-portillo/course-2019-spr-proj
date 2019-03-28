import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class Get_US_Holidays(dml.Algorithm):
    contributor = 'hxjia_jiahaozh'
    reads = []
    writes = ['hxjia_jiahaozh.US_Holidays']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')

        url = "http://datamechanics.io/data/hxjia_jiahaozh/US_Holidays.csv"
#        response = urllib.request.urlopen(url).read().decode("utf-8")
        uh = pd.read_csv(url)
        new_uh = pd.DataFrame(
            {'Date': uh['Date'],
             'Holiday': uh['Holiday']
             })
        r = json.loads(new_uh.to_json(orient='records'))
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("US_Holidays")
        repo.createCollection("US_Holidays")
        repo['hxjia_jiahaozh.US_Holidays'].insert_many(r)
        repo['hxjia_jiahaozh.US_Holidays'].metadata({'complete': True})
        print(repo['hxjia_jiahaozh.US_Holidays'].metadata())

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
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/hxjia_jiahaozh/usholidays')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/hjia_jiahaozh/holidays')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/hxjia_jiahaozh/')

        this_script = doc.agent('alg:hxjia_jiahaozh#get_us_holidays',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:US_Holidays',
                              {'prov:label': 'US_Holidays, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_holidays = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_holidays, this_script)
        doc.usage(get_holidays, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=US+Holidays&$select=Date,Holiday'
                   }
                  )

        holidays = doc.entity('dat:hxjia_jiahaozh#holidays',
                          {prov.model.PROV_LABEL: 'US_Holidays', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(holidays, this_script)
        doc.wasGeneratedBy(holidays, get_holidays, endTime)
        doc.wasDerivedFrom(holidays, resource, get_holidays, get_holidays, get_holidays)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Get_US_Holidays.execute()
# doc = US_Holidays.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class boston_crime_incidents(dml.Algorithm):
    contributor = 'hek_kquirk'
    reads = []
    writes = ['hek_kquirk.boston_crime_incidents']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hek_kquirk', 'hek_kquirk')

        # Drop/recreate mongo collection
        repo.dropCollection("boston_crime_incidents")
        repo.createCollection("boston_crime_incidents")

        # Api call for employee earnings dataset
        url = 'https://data.boston.gov/api/3/action/datastore_search?resource_id=12cb3883-56f5-47de-afa5-3b1cf61b257b&limit=30000'

        # Can only get 100 entries at a time. Keep querying until there are
        # no more entries.
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)['result']
        repo['hek_kquirk.boston_crime_incidents'].insert_many(r['records'])
        while len(r['records']) > 0 and 'next' in r['_links']:
            url = 'https://data.boston.gov' + r['_links']['next']
            response = urllib.request.urlopen(url).read().decode("utf-8")
            r = json.loads(response)['result']
            if len(r['records']) > 0:
                repo['hek_kquirk.boston_crime_incidents'].insert_many(r['records'])
        
        repo['hek_kquirk.boston_crime_incidents'].metadata({'complete':True})
        print(repo['hek_kquirk.boston_crime_incidents'].metadata())

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
        repo.authenticate('hek_kquirk', 'hek_kquirk')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/')

        this_script = doc.agent('alg:hek_kquirk#boston_crime_incidents', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        resource = doc.entity('bdp:api/3/datastore_search/', {'prov:label':'Boston Open Data search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_boston_crime_incidents = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_boston_crime_incidents, this_script)
        doc.usage(get_boston_crime_incidents, resource, startTime, None,
                {
                      prov.model.PROV_TYPE:'ont:Retrieval',
                      'ont:Query':'?resource_id=12cb3883-56f5-47de-afa5-3b1cf61b257b'
                  }
        )
        
        boston_crime_incidents = doc.entity('dat:hek_kquirk#boston_crime_incidents', {prov.model.PROV_LABEL:'Boston Crime Incidents', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(boston_crime_incidents, this_script)
        doc.wasGeneratedBy(boston_crime_incidents, get_boston_crime_incidents, endTime)
        doc.wasDerivedFrom(boston_crime_incidents, resource, get_boston_crime_incidents, get_boston_crime_incidents, get_boston_crime_incidents)

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

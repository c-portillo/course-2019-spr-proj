import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class boston_employee_earnings(dml.Algorithm):
    contributor = 'hek_kquirk'
    reads = []
    writes = ['hek_kquirk.boston_employee_earnings']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hek_kquirk', 'hek_kquirk')

        # Drop/recreate mongo collection
        repo.dropCollection("boston_employee_earnings")
        repo.createCollection("boston_employee_earnings")

        # Api call for employee earnings dataset
        url = 'https://data.boston.gov/api/3/action/datastore_search?resource_id=70129b87-bd4e-49bb-aa09-77644da73503&limit=30000'

        # Can only get 100 entries at a time. Keep querying until there are
        # no more entries.
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)['result']
        repo['hek_kquirk.boston_employee_earnings'].insert_many(r['records'])
        while len(r['records']) > 0 and 'next' in r['_links']:
            url = 'https://data.boston.gov' + r['_links']['next']
            response = urllib.request.urlopen(url).read().decode("utf-8")
            r = json.loads(response)['result']
            if len(r['records']) > 0:
                repo['hek_kquirk.boston_employee_earnings'].insert_many(r['records'])
                
        repo['hek_kquirk.boston_employee_earnings'].metadata({'complete':True})
        print(repo['hek_kquirk.boston_employee_earnings'].metadata())

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

        this_script = doc.agent('alg:hek_kquirk#boston_employee_earnings', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        resource = doc.entity('bdp:api/3/datastore_search/', {'prov:label':'Boston Open Data search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_boston_employee_earnings = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_boston_employee_earnings, this_script)
        doc.usage(get_boston_employee_earnings, resource, startTime, None,
                  {
                      prov.model.PROV_TYPE:'ont:Retrieval',
                    'ont:Query':'?resource_id=70129b87-bd4e-49bb-aa09-77644da73503'
                  }
        )
        
        boston_employee_earnings = doc.entity('dat:hek_kquirk#boston_employee_earnings', {prov.model.PROV_LABEL:'Boston Employee Earnings', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(boston_employee_earnings, this_script)
        doc.wasGeneratedBy(boston_employee_earnings, get_boston_employee_earnings, endTime)
        doc.wasDerivedFrom(boston_employee_earnings, resource, get_boston_employee_earnings, get_boston_employee_earnings, get_boston_employee_earnings)

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

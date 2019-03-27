import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class bpd_fio(dml.Algorithm):
    contributor = 'hek_kquirk'
    reads = []
    writes = ['hek_kquirk.bpd_fio']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hek_kquirk', 'hek_kquirk')

        # Drop/recreate mongo collection
        repo.dropCollection("bpd_fio")
        repo.createCollection("bpd_fio")

        # Api call for employee earnings dataset
        url = 'https://data.boston.gov/api/3/action/datastore_search?resource_id=35f3fb8f-4a01-4242-9758-f664e7ead125&limit=30000'
            
        # Can only get 100 entries at a time. Keep querying until there are
        # no more entries.
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)['result']
        repo['hek_kquirk.bpd_fio'].insert_many(r['records'])
        while len(r['records']) > 0 and 'next' in r['_links']:
            url = 'https://data.boston.gov' + r['_links']['next']
            response = urllib.request.urlopen(url).read().decode("utf-8")
            r = json.loads(response)['result']
            if len(r['records']) > 0:
                repo['hek_kquirk.bpd_fio'].insert_many(r['records'])
                
            
        repo['hek_kquirk.bpd_fio'].metadata({'complete':True})
        print(repo['hek_kquirk.bpd_fio'].metadata())

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
        
        this_script = doc.agent('alg:hek_kquirk#bpd_fio', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        resource = doc.entity('bdp:api/3/datastore_search/', {'prov:label':'Boston Open Data search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_bpd_fio = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_bpd_fio, this_script)
        doc.usage(get_bpd_fio, resource, startTime, None,
                  {
                      prov.model.PROV_TYPE:'ont:Retrieval',
                      'ont:Query':'?resource_id=35f3fb8f-4a01-4242-9758-f664e7ead125'
                  }
        )

        bpd_fio = doc.entity('dat:hek_kquirk#bpd_fio', {prov.model.PROV_LABEL:'BPD Field Interigation and Observation', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bpd_fio, this_script)
        doc.wasGeneratedBy(bpd_fio, get_bpd_fio, endTime)
        doc.wasDerivedFrom(bpd_fio, resource, get_bpd_fio, get_bpd_fio, get_bpd_fio)

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

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class health_uber_input(dml.Algorithm):
    contributor = 'chuci_yfch_yuwan_zhurh'
    reads = []
    writes = ['chuci_yfch_yuwan_zhurh.uber', 'chuci_yfch_yuwan_zhurh.health']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        # Get the uber dataset
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        url = 'https://raw.githubusercontent.com/yizheshexin/504_uber_json/master/uber_newcity_cc.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("uber")
        repo.createCollection("uber")
        repo['chuci_yfch_yuwan_zhurh.uber'].insert_many(r)
        repo['chuci_yfch_yuwan_zhurh.uber'].metadata({'complete': True})

        # Get the health dataset

        url2 = 'http://datamechanics.io/data/health_new_int_cc.json'
        response2 = urllib.request.urlopen(url2).read().decode("utf-8")
        r2 = json.loads(response2)
        s2 = json.dumps(r2, sort_keys=True, indent=2)
        repo.dropCollection("health")
        repo.createCollection("health")
        repo['chuci_yfch_yuwan_zhurh.health'].insert_many(r2)
        repo['chuci_yfch_yuwan_zhurh.health'].metadata({'complete': True})

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
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://chronicdata.cdc.gov/')

        this_script = doc.agent('alg:chuci_yfch_yuwan_zhurh#health_uber_input', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:onlinedata', {'prov:label':'Online Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_health = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_uber = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_health, this_script)
        doc.wasAssociatedWith(get_uber, this_script)
        doc.usage(get_health, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )
        doc.usage(get_uber, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+Lost&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )

        uber = doc.entity('dat:chuci_yfch_yuwan_zhurh#uber', {prov.model.PROV_LABEL:'uber data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(uber, this_script)
        doc.wasGeneratedBy(uber, get_uber, endTime)
        doc.wasDerivedFrom(resource, uber, get_uber, get_uber, get_uber)

        health = doc.entity('dat:chuci_yfch_yuwan_zhurh#health', {prov.model.PROV_LABEL:'health data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(health, this_script)
        doc.wasGeneratedBy(health, get_health, endTime)
        doc.wasDerivedFrom(resource, health, get_health, get_health, get_health)

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
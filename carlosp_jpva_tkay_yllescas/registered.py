import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class registered(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = []
    writes = ['carlosp_jpva_tkay_yllescas.registered']

    @staticmethod
    def execute(trial = False):
        print("registered")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()
        
        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        
        file = 'data/registered_voters_xtabs.json'
        with open(file, "r", encoding = "utf8") as datafile:
            json_string = datafile.read()
        r = json.loads(json_string)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("registered")
        repo.createCollection("registered")
        repo['carlosp_jpva_tkay_yllescas.registered'].insert_many(r)
        repo['carlosp_jpva_tkay_yllescas.registered'].metadata({'complete':True})
        print(repo['carlosp_jpva_tkay_yllescas.registered'].metadata())
        
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
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#registered', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_registered = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_registered, this_script)
        doc.usage(get_registered, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Registered&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )

        registered = doc.entity('dat:carlosp_jpva_tkay_yllescas#registered', {prov.model.PROV_LABEL:'Registered Voters', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(registered, this_script)
        doc.wasGeneratedBy(registered, get_registered, endTime)
        doc.wasDerivedFrom(registered, resource, get_registered, get_registered, get_registered)

        repo.logout()
                  
        return doc
    
#registered.execute()

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv 
import io
#get the data about neighborhoods

class poverty(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = []
    writes = ['henryhcy_wangyp.poverty']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        url = 'http://datamechanics.io/data/henryhcy_wangyp/poverty_rates.json'      
        # parse the data as following
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("poverty")
        repo.createCollection("poverty")
        repo['henryhcy_wangyp.poverty'].insert_many(r)
        repo['henryhcy_wangyp.poverty'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.poverty'].metadata())
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
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/henryhcy_wangyp/')

        this_script = doc.agent('alg:henryhcy_wangyp#poverty', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:poverty_rates.json', {'prov:label':'poverty information', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_poverty = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_poverty, this_script)
        doc.usage(get_poverty, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=poverty&$select=name,address,city,state,location,OPEN_DT'
                  }
                  )
        

        poverty = doc.entity('dat:henryhcy_wangyp#poverty', {prov.model.PROV_LABEL:'poverty', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(poverty, this_script)
        doc.wasGeneratedBy(poverty, get_poverty, endTime)
        doc.wasDerivedFrom(poverty, resource, get_poverty, get_poverty, get_poverty)

        

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
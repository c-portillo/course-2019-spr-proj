
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv 
import io
#get the data about neighborhoods

class income(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = []
    writes = ['henryhcy_wangyp.income']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
       

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        url = 'http://datamechanics.io/data/henryhcy_wangyp/household_income.json'      
        # parse the data as following
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("income")
        repo.createCollection("income")
        repo['henryhcy_wangyp.income'].insert_many(r)
        repo['henryhcy_wangyp.income'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.income'].metadata())
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

        this_script = doc.agent('alg:henryhcy_wangyp#income', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:household_income.json', {'prov:label':'income information', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_income = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_income, this_script)
        doc.usage(get_income, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=income&$select=name,address,city,state,location,OPEN_DT'
                  }
                  )
        

        income = doc.entity('dat:henryhcy_wangyp#income', {prov.model.PROV_LABEL:'income', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(income, this_script)
        doc.wasGeneratedBy(income, get_income, endTime)
        doc.wasDerivedFrom(income, resource, get_income, get_income, get_income)

        

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
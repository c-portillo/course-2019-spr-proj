import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import bson.code

class bpd_employee_earnings(dml.Algorithm):
    contributor = 'hek_kquirk'
    reads = ['hek_kquirk.boston_employee_earnings']
    writes = ['hek_kquirk.bpd_employee_earnings']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hek_kquirk', 'hek_kquirk')

        # Drop/recreate mongo collection
        repo.dropCollection("bpd_employee_earnings")
        repo.createCollection("bpd_employee_earnings")

        bpd_earnings = repo['hek_kquirk.boston_employee_earnings'].find({'DEPARTMENT NAME': 'Boston Police Department'})
        repo['hek_kquirk.bpd_employee_earnings'].insert_many(bpd_earnings)
        
        repo['hek_kquirk.bpd_employee_earnings'].metadata({'complete':True})
        print(repo['hek_kquirk.bpd_employee_earnings'].metadata())

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

        this_script = doc.agent('alg:hek_kquirk#bpd_employee_earnings', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        resource = doc.entity('dat:hek_kquirk#boston_employee_earnings', {'prov:label':'Boston Open Data search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_bpd_employee_earnings = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_bpd_employee_earnings, this_script)
        doc.usage(get_bpd_employee_earnings, resource, startTime, None,
                  {
                      prov.model.PROV_TYPE:'ont:Computation'
                  }
        )
        
        bpd_employee_earnings = doc.entity('dat:hek_kquirk#bpd_employee_earnings', {prov.model.PROV_LABEL:'BPD Employee Earnings', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bpd_employee_earnings, this_script)
        doc.wasGeneratedBy(bpd_employee_earnings, get_bpd_employee_earnings, endTime)
        doc.wasDerivedFrom(bpd_employee_earnings, resource, get_bpd_employee_earnings, get_bpd_employee_earnings, get_bpd_employee_earnings)

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

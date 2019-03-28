import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests

class example(dml.Algorithm):
    contributor = 'arshadr_rcallah_shaikh1'
    reads = []
    #writes = ['arshadr_rcallah_shaikh1.assessor18', 'arshadr_rcallah_shaikh1.permits', 'arshadr_rcallah_shaikh1.incomes']
    writes = ['arshadr_rcallah_shaikh1.permits', 'arshadr_rcallah_shaikh1.permits', 'arshadr_rcallah_shaikh1.incomes']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('arshadr_rcallah_shaikh1', 'arshadr_rcallah_shaikh1')

        url = 'http://datamechanics.io/data/arshadr_rcallah_shaikh1/24a90fa2-d3b1-4857-acc1-fbcae3e2cc91.json'
        response = urllib.request.urlopen(url).read().decode("utf-8", errors = 'replace')
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("permits")
        repo.createCollection("permits")
        repo['arshadr_rcallah_shaikh1.permits'].insert_one(r)
        repo['arshadr_rcallah_shaikh1.permits'].metadata({'complete':True})
        print(repo['arshadr_rcallah_shaikh1.permits'].metadata())

        
        url = "http://datamechanics.io/data/arshadr_rcallah_shaikh1/ChelseaAssessorsDatabase2018.json"
        response = urllib.request.urlopen(url).read().decode("utf-8", errors = 'replace')
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("assessor18")
        repo.createCollection("assessor18")
        repo['arshadr_rcallah_shaikh1.assessor18'].insert_one(r)


        url = "http://datamechanics.io/data/arshadr_rcallah_shaikh1/income-in-the-past-12-months.json"
        response = urllib.request.urlopen(url).read().decode("utf-8", errors = 'replace')
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("incomes")
        repo.createCollection("incomes")
        repo['arshadr_rcallah_shaikh1.incomes'].insert_one(r)

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
        repo.authenticate('arshadr_rcallah_shaikh1', 'arshadr_rcallah_shaikh1')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('drv', 'https://drive.google.com/')
        doc.add_namespace('chl', 'https://chelseama.ogopendata.com/dataset/')
        doc.add_namespace('chl', 'https://chelseama.ogopendata.com/dataset/')

        this_script = doc.agent('alg:arshadr_rcallah_shaikh1#example', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('drv:file/d/1kiukuGI3Kl5qBzsKHOtCW17DdhaCLiMY/view', { prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource = doc.entity('chl:building-permits-2016-onwards/resource/24a90fa2-d3b1-4857-acc1-fbcae3e2cc91', { prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource = doc.entity('chl:chelsea-residents-incomes-in-the-past-12-months/resource/659c4348-6b39-4b79-8483-1f3ced5389c9', { prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_assessor18 = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_permits = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_incomes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_assessor18, this_script)
        doc.wasAssociatedWith(get_permits, this_script)
        doc.wasAssociatedWith(get_incomes, this_script)
        doc.usage(get_assessor18, resource, startTime, None,
                 {prov.model.PROV_TYPE:'ont:Retrieval',
                   'ont:Retrieval':''
                   }
                  )
        doc.usage(get_permits, resource, startTime, None,
                   {prov.model.PROV_TYPE:'ont:Retrieval',
                   'ont:Retrieval':''
                   }
                  )
        doc.usage(get_incomes, resource, startTime, None,
                   {prov.model.PROV_TYPE:'ont:Retrieval',
                   'ont:Retrieval':''
                   }
                  )
        assessor18 = doc.entity('dat:arshadr_rcallah_shaikh1#assessor18', {prov.model.PROV_LABEL:'Assessors Office', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(assessor18, this_script)
        doc.wasGeneratedBy(assessor18, get_assessor18, endTime)
        doc.wasDerivedFrom(assessor18, resource, get_assessor18, get_assessor18, get_assessor18)

        permits = doc.entity('dat:arshadr_rcallah_shaikh1#permits', {prov.model.PROV_LABEL:'Building Permits', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(permits, this_script)
        doc.wasGeneratedBy(permits, get_permits, endTime)
        doc.wasDerivedFrom(permits, resource, get_permits, get_permits, get_permits)

        incomes = doc.entity('dat:arshadr_rcallah_shaikh1#incomes', {prov.model.PROV_LABEL:'Resident Incomes', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(incomes, this_script)
        doc.wasGeneratedBy(incomes, get_incomes, endTime)
        doc.wasDerivedFrom(incomes, resource, get_incomes, get_incomes, get_incomes)


        repo.logout()
                  
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# example.execute()
'''
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
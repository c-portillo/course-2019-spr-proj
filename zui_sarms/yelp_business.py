import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class yelp_business(dml.Algorithm):
    contributor = 'zui_sarms'
    reads = []
    writes = ['zui_sarms.yelp_business']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')

        url = 'http://datamechanics.io/data/businesses.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("yelp_business")
        repo.createCollection("yelp_business")
        repo['zui_sarms.yelp_business'].insert_many(r)
        repo['zui_sarms.yelp_business'].metadata({'complete':True})
        print(repo['zui_sarms.yelp_business'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:zui_sarms#yelp_business', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:business.json', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_business = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_business, this_script)
        doc.usage(get_business, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        yelp_business = doc.entity('dat:zui_sarms#yelp_business', {prov.model.PROV_LABEL:'Yelp Businesses', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(yelp_business, this_script)
        doc.wasGeneratedBy(yelp_business, get_business, endTime)
        doc.wasDerivedFrom(yelp_business, resource, get_business, get_business, get_business)

        repo.logout()
                  
        return doc

## eof
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class getZipcodes(dml.Algorithm):
    contributor = 'misn15'
    reads = []
    writes = ['misn15.zipcodes']

    @staticmethod
    def execute(trial = False):
        '''Retrieve zip codes for city of Boston'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('misn15', 'misn15')

        url = 'http://datamechanics.io/data/zip_tracts.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)      
        repo.dropCollection("zipcodes")
        repo.createCollection("zipcodes")
        repo['misn15.zipcodes'].insert_many(r)
        repo['misn15.zipcodes'].metadata({'complete':True})
        print(repo['misn15.zipcodes'].metadata())

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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('census', 'https://www.census.gov/geo/reference/codes/cou.html')

        this_script = doc.agent('alg:misn15#getZipcodes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('census:Boston_zipcodes', {'prov:label':'Boston_zipcodes', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_zipcodes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_zipcodes, this_script)
        doc.usage(get_zipcodes, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )
        zipcodes_data = doc.entity('dat:misn15#getZipcodes', {prov.model.PROV_LABEL:'Boston Crime', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(zipcodes_data, this_script)
        doc.wasGeneratedBy(zipcodes_data, get_zipcodes, endTime)
        doc.wasDerivedFrom(zipcodes_data, resource, get_zipcodes, get_zipcodes, get_zipcodes)
                  
        return doc


getZipcodes.execute()
doc = getZipcodes.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof

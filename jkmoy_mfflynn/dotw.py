import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

def project(R, p):
    return [p(t) for t in R]

def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k,v) in R if k == key])) for key in keys]

class dotw(dml.Algorithm):
    contributor = 'jkmoy_mfflynn'
    reads = ['jkmoy_mfflynn.crime']
    writes = ['jkmoy_mfflynn.dotw']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')

        # transformation here
        collection = list(repo['jkmoy_mfflynn.crime'].find())
        
        total = len(collection)
        
        data = [(doc['day_of_week'], 1) for doc in collection if doc['day_of_week'].strip != '']
        data = project(aggregate(data, sum), lambda t: (t[0], t[1], t[1]/500))

        finalDataset = [{'dotw':tup[0],'count':tup[1],'percent':tup[2]} for tup in data]
        for x  in finalDataset:
            print(x)
        
        repo.dropCollection('jkmoy_mfflynn.dotw')
        repo.createCollection('jkmoy_mfflynn.dotw')
        
        repo['jkmoy_mfflynn.dotw'].insert_many(finalDataset)
        repo['jkmoy_mfflynn.dotw'].metadata({'complete': True})

        print(repo['jkmoy_mfflynn.dotw'].metadata())
        
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
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/jkmoy_mfflynn') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/jkmoy_mfflynn') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:jkmoy_mfflynn#dotw', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:dotwAvg', {'prov:label':'Crimes by dotw', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_dotw = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_dotw, this_script)
        doc.usage(get_dotw, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'})

        dotw = doc.entity('dat:jkmoy_mfflynn#dotws', {prov.model.PROV_LABEL:'Crime dotw %', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(dotw, this_script)
        doc.wasGeneratedBy(dotw, get_dotw, endTime)
        doc.wasDerivedFrom(dotw, resource, get_dotw, get_dotw, get_dotw)

        repo.logout()
                  
        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
averagePerDepartment.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
#dotw.execute()

## eof

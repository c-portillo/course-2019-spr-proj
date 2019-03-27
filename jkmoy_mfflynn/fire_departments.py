import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class fire_departments(dml.Algorithm):
    contributor = 'jkmoy_mfflynn'
    reads = []
    writes = ['jkmoy_mfflynn.fire_departments']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')

        url = 'http://gis.cityofboston.gov/arcgis/rest/services/PublicSafety/OpenData/MapServer/2/query?where=1%3D1&outFields=*&outSR=4326&f=json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        r = r['features']#[0]['attributes'] # this needed?
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("jkmoy_mfflynn.fire_departments")
        repo.createCollection("jkmoy_mfflynn.fire_departments")
        repo['jkmoy_mfflynn.fire_departments'].insert_many(r)
        repo['jkmoy_mfflynn.fire_departments'].metadata({'complete':True})
        print(repo['jkmoy_mfflynn.fire_departments'].metadata())

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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('fire', 'https://data.boston.gov/datastore/odata3.0/220a4ce5-a991-4336-a19b-159881d7c2e7?$format=json')
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/') # remove?

        this_script = doc.agent('alg:jkmoy_mfflynn#fire_departments', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:fire_department', {'prov:label':'Different Fire Departments', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_fire_departments = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fire_departments, this_script)
        doc.usage(get_fire_departments, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'})

        fire_departments = doc.entity('dat:jkmoy_mfflynn#fire_departments', {prov.model.PROV_LABEL:'Boston Fire Departments', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(fire_departments, this_script)
        doc.wasGeneratedBy(fire_departments, get_fire_departments, endTime)
        doc.wasDerivedFrom(fire_departments, resource, get_fire_departments, get_fire_departments, get_fire_departments)

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

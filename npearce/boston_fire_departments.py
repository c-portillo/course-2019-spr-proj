import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class boston_fire_departments(dml.Algorithm):
    contributor = 'npearce'
    reads = []
    writes = ['npearce.boston_fire_departments']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('npearce', 'npearce')

        # Drop and create mongo collection
        repo.dropCollection("boston_fire_departments")
        repo.createCollection("boston_fire_departments")
        
        # API call for fire departments dataset
        url = 'https://opendata.arcgis.com/datasets/092857c15cbb49e8b214ca5e228317a1_2.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        features = json.loads(response)['features']
        
        # Collect point tuples in pts
        pts = []
        for feature in features:
            coords = feature['geometry']['coordinates']
            pt = {'coordinates':coords}
            pts.append(pt)
        repo['npearce.boston_fire_departments'].insert_many(pts)
        repo['npearce.boston_fire_departments'].create_index([('coordinates', dml.pymongo.GEO2D)])
        
        repo['npearce.boston_fire_departments'].metadata({'complete':True})
        print(repo['npearce.boston_fire_departments'].metadata())
        
        repo.logout()
        
        endTime = datetime.datetime.now()
        
        return {'start':startTime, 'end':endTime}
    
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
        repo.authenticate('npearce', 'npearce')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:npearce#boston_fire_departments', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:092857c15cbb49e8b214ca5e228317a1_2', {'prov:label':'Fire Departments', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        get_fds = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fds, this_script)
        doc.usage(get_fds, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Point&$select=coordinates'
                  }
                  )

        fire_departments = doc.entity('dat:npearce#boston_fire_departments', {prov.model.PROV_LABEL:'Fire Departments', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(fire_departments, this_script)
        doc.wasGeneratedBy(fire_departments, get_fds, endTime)
        doc.wasDerivedFrom(fire_departments, resource, get_fds, get_fds, get_fds)

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
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class boston_fire_alarm_boxes(dml.Algorithm):
    contributor = 'npearce'
    reads = []
    writes = ['npearce.boston_fire_alarm_boxes']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('npearce', 'npearce')

        # Drop and create mongo collection
        repo.dropCollection("boston_fire_alarm_boxes")
        repo.createCollection("boston_fire_alarm_boxes")
        
        # API call for fire departments dataset
        url = 'https://opendata.arcgis.com/datasets/3a0f4db1e63a4a98a456fdb71dc37a81_1.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        features = json.loads(response)['features']
        
        # Collect point tuples in pts
        pts = []
        for feature in features:
            coords = feature['geometry']['coordinates']
            pt = {'coordinates':coords}
            pts.append(pt)
        repo['npearce.boston_fire_alarm_boxes'].insert_many(pts)
        repo['npearce.boston_fire_alarm_boxes'].create_index([('coordinates', dml.pymongo.GEO2D)])
        
        repo['npearce.boston_fire_alarm_boxes'].metadata({'complete':True})
        print(repo['npearce.boston_fire_alarm_boxes'].metadata())
        
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

        this_script = doc.agent('alg:npearce#boston_fire_alarm_boxes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:3a0f4db1e63a4a98a456fdb71dc37a81_1', {'prov:label':'Fire Alarm Boxes', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        get_fabs = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fabs, this_script)
        doc.usage(get_fabs, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Point&$select=coordinates'
                  }
                  )

        fire_alarm_boxes = doc.entity('dat:npearce#boston_fire_alarm_boxes', {prov.model.PROV_LABEL:'Fire Alarm Boxes', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(fire_alarm_boxes, this_script)
        doc.wasGeneratedBy(fire_alarm_boxes, get_fabs, endTime)
        doc.wasDerivedFrom(fire_alarm_boxes, resource, get_fabs, get_fabs, get_fabs)

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
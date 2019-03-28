#import urllib.request
#import json
import dml
import prov.model
import datetime
import uuid

from bson.son import SON

class nearby_alarm_boxes(dml.Algorithm):
    contributor = 'npearce'
    reads = ['npearce.boston_fire_alarm_boxes', 'npearce.boston_public_schools', 'npearce.boston_nonpublic_schools']
    writes = ['npearce.ps_alarm_boxes', 'npearce.nps_alarm_boxes']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('npearce', 'npearce')

        # Drop and create mongo collections
        repo.dropCollection('ps_alarm_boxes')
        repo.createCollection('ps_alarm_boxes')
        repo.dropCollection('nps_alarm_boxes')
        repo.createCollection('nps_alarm_boxes')
        
        # Read public school locations
        pss = repo['npearce.boston_public_schools'].find()
        
        # Collect nearby alarm box counts in counts
        counts = []
        for ps in pss:
            coords = ps['coordinates']
            query = {'coordinates': SON([('$near', coords), 
                                         ('$maxDistance', 0.00724637681159)])}
            c = repo['npearce.boston_fire_alarm_boxes'].find(query).count()
            counts.append({'count': c})
        repo['npearce.ps_alarm_boxes'].insert_many(counts)
        
        repo['npearce.ps_alarm_boxes'].metadata({'complete':True})
        print(repo['npearce.ps_alarm_boxes'].metadata())
        
        # Read non public school locations
        npss = repo['npearce.boston_nonpublic_schools'].find()
        
        # Collect nearby alarm box counts in counts
        counts = []
        for nps in npss:
            coords = nps['coordinates']
            query = {'coordinates': SON([('$near', coords), 
                                         ('$maxDistance', 0.00724637681159)])}
            c = repo['npearce.boston_fire_alarm_boxes'].find(query).count()
            counts.append({'count': c})
        repo['npearce.nps_alarm_boxes'].insert_many(counts)
        
        repo['npearce.nps_alarm_boxes'].metadata({'complete':True})
        print(repo['npearce.nps_alarm_boxes'].metadata())
        
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

        this_script = doc.agent('alg:npearce#nearby_alarm_boxes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_nonpublic_schools = doc.entity('dat:npearce#boston_nonpublic_schools', {prov.model.PROV_LABEL:'Nonpublic Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_public_schools = doc.entity('dat:npearce#boston_public_schools', {prov.model.PROV_LABEL:'Public Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_fire_alarm_boxes = doc.entity('dat:npearce#boston_fire_alarm_boxes', {prov.model.PROV_LABEL:'Fire Alarm Boxes', prov.model.PROV_TYPE:'ont:DataSet'})
        
        get_nearby_boxes_nps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nearby_boxes_nps, this_script)
        doc.usage(get_nearby_boxes_nps, resource_nonpublic_schools, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_nearby_boxes_nps, resource_fire_alarm_boxes, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        
        get_nearby_boxes_ps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nearby_boxes_ps, this_script)
        doc.usage(get_nearby_boxes_ps, resource_public_schools, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_nearby_boxes_ps, resource_fire_alarm_boxes, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})

        nearby_alarm_boxes_p = doc.entity('dat:npearce#ps_alarm_boxes', {prov.model.PROV_LABEL:'Public Nearby Alarm Boxes', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nearby_alarm_boxes_p, this_script)
        doc.wasGeneratedBy(nearby_alarm_boxes_p, get_nearby_boxes_ps, endTime)
        doc.wasDerivedFrom(nearby_alarm_boxes_p, resource_public_schools, get_nearby_boxes_ps, get_nearby_boxes_ps, get_nearby_boxes_ps)
        doc.wasDerivedFrom(nearby_alarm_boxes_p, resource_fire_alarm_boxes, get_nearby_boxes_ps, get_nearby_boxes_ps, get_nearby_boxes_ps)
        
        nearby_alarm_boxes_np = doc.entity('dat:npearce#nps_alarm_boxes', {prov.model.PROV_LABEL:'Nonpublic Nearby Alarm Boxes', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nearby_alarm_boxes_np, this_script)
        doc.wasGeneratedBy(nearby_alarm_boxes_np, get_nearby_boxes_nps, endTime)
        doc.wasDerivedFrom(nearby_alarm_boxes_np, resource_nonpublic_schools, get_nearby_boxes_nps, get_nearby_boxes_nps, get_nearby_boxes_nps)
        doc.wasDerivedFrom(nearby_alarm_boxes_np, resource_fire_alarm_boxes, get_nearby_boxes_nps, get_nearby_boxes_nps, get_nearby_boxes_nps)

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
#import urllib.request
#import json
import dml
import prov.model
import datetime
import uuid
import math

class nearest_departments(dml.Algorithm):
    contributor = 'npearce'
    reads = ['npearce.boston_fire_departments', 'npearce.boston_public_schools', 'npearce.boston_nonpublic_schools']
    writes = ['npearce.ps_departments', 'npearce.nps_departments']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('npearce', 'npearce')

        # Drop and create mongo collections
        repo.dropCollection('ps_departments')
        repo.createCollection('ps_departments')
        repo.dropCollection('nps_departments')
        repo.createCollection('nps_departments')
        
        # Read public school locations
        pss = repo['npearce.boston_public_schools'].find()
        
        # Collect distances to nearest department in dists
        dists = []
        for ps in pss:
            coords = ps['coordinates']
            query = {'coordinates': {'$near': coords}}
            nearest = repo['npearce.boston_fire_departments'].find(query).limit(1)
            
            x1, y1 = coords
            x2, y2 = nearest[0]['coordinates']
            dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            dists.append({'minDistance': dist})
        repo['npearce.ps_departments'].insert_many(dists)
        
        repo['npearce.ps_departments'].metadata({'complete':True})
        print(repo['npearce.ps_departments'].metadata())
        
        # Read non public school locations
        npss = repo['npearce.boston_nonpublic_schools'].find()
        
        # Collect distances to nearest department in dists
        dists = []
        for nps in npss:
            coords = nps['coordinates']
            query = {'coordinates': {'$near': coords}}
            nearest = repo['npearce.boston_fire_departments'].find(query).limit(1)
            
            x1, y1 = coords
            x2, y2 = nearest[0]['coordinates']
            dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            dists.append({'minDistance': dist})
        repo['npearce.nps_departments'].insert_many(dists)
        
        repo['npearce.nps_departments'].metadata({'complete':True})
        print(repo['npearce.nps_departments'].metadata())
        
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

        this_script = doc.agent('alg:npearce#nearest_departments', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_nonpublic_schools = doc.entity('dat:npearce#boston_nonpublic_schools', {prov.model.PROV_LABEL:'Nonpublic Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_public_schools = doc.entity('dat:npearce#boston_public_schools', {prov.model.PROV_LABEL:'Public Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_fire_departments = doc.entity('dat:npearce#boston_fire_departments', {prov.model.PROV_LABEL:'Fire Departments', prov.model.PROV_TYPE:'ont:DataSet'})
        
        get_nearest_departments_nps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nearest_departments_nps, this_script)
        doc.usage(get_nearest_departments_nps, resource_nonpublic_schools, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_nearest_departments_nps, resource_fire_departments, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        
        get_nearest_departments_ps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nearest_departments_ps, this_script)
        doc.usage(get_nearest_departments_ps, resource_public_schools, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_nearest_departments_ps, resource_fire_departments, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})

        nearest_departments_p = doc.entity('dat:npearce#ps_departments', {prov.model.PROV_LABEL:'Public Nearby Departments', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nearest_departments_p, this_script)
        doc.wasGeneratedBy(nearest_departments_p, get_nearest_departments_ps, endTime)
        doc.wasDerivedFrom(nearest_departments_p, resource_public_schools, get_nearest_departments_ps, get_nearest_departments_ps, get_nearest_departments_ps)
        doc.wasDerivedFrom(nearest_departments_p, resource_fire_departments, get_nearest_departments_ps, get_nearest_departments_ps, get_nearest_departments_ps)
        
        nearest_departments_np = doc.entity('dat:npearce#nps_departments', {prov.model.PROV_LABEL:'Nonpublic Nearby Departments', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nearest_departments_np, this_script)
        doc.wasGeneratedBy(nearest_departments_np, get_nearest_departments_nps, endTime)
        doc.wasDerivedFrom(nearest_departments_np, resource_nonpublic_schools, get_nearest_departments_nps, get_nearest_departments_nps, get_nearest_departments_nps)
        doc.wasDerivedFrom(nearest_departments_np, resource_fire_departments, get_nearest_departments_nps, get_nearest_departments_nps, get_nearest_departments_nps)
               
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
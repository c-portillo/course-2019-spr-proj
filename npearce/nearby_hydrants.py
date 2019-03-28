#import urllib.request
#import json
import dml
import prov.model
import datetime
import uuid

from bson.son import SON

class nearby_hydrants(dml.Algorithm):
    contributor = 'npearce'
    reads = ['npearce.boston_fire_hydrants', 'npearce.boston_public_schools', 'npearce.boston_nonpublic_schools']
    writes = ['npearce.ps_hydrants', 'npearce.nps_hydrants']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('npearce', 'npearce')

        # Drop and create mongo collections
        repo.dropCollection('ps_hydrants')
        repo.createCollection('ps_hydrants')
        repo.dropCollection('nps_hydrants')
        repo.createCollection('nps_hydrants')
        
        # Read public school locations
        pss = repo['npearce.boston_public_schools'].find()
        
        # Collect nearby hydrant counts in counts
        counts = []
        for ps in pss:
            coords = ps['coordinates']
            query = {'coordinates': SON([('$near', coords), 
                                         ('$maxDistance', 0.00724637681159)])}
            c = repo['npearce.boston_fire_hydrants'].find(query).count()
            counts.append({'count': c})
        repo['npearce.ps_hydrants'].insert_many(counts)
        
        repo['npearce.ps_hydrants'].metadata({'complete':True})
        print(repo['npearce.ps_hydrants'].metadata())
        
        # Read non public school locations
        npss = repo['npearce.boston_nonpublic_schools'].find()
        
        # Collect nearby hydrant counts in counts
        counts = []
        for nps in npss:
            coords = nps['coordinates']
            query = {'coordinates': SON([('$near', coords), 
                                         ('$maxDistance', 0.00724637681159)])}
            c = repo['npearce.boston_fire_hydrants'].find(query).count()
            counts.append({'count': c})
        repo['npearce.nps_hydrants'].insert_many(counts)
        
        repo['npearce.nps_hydrants'].metadata({'complete':True})
        print(repo['npearce.nps_hydrants'].metadata())
        
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

        this_script = doc.agent('alg:npearce#nearby_hydrants', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_nonpublic_schools = doc.entity('dat:npearce#boston_nonpublic_schools', {prov.model.PROV_LABEL:'Nonpublic Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_public_schools = doc.entity('dat:npearce#boston_public_schools', {prov.model.PROV_LABEL:'Public Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_fire_hydrants = doc.entity('dat:npearce#boston_fire_hydrants', {prov.model.PROV_LABEL:'Fire Hydrants', prov.model.PROV_TYPE:'ont:DataSet'})
        
        get_nearby_hydrants_nps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nearby_hydrants_nps, this_script)
        doc.usage(get_nearby_hydrants_nps, resource_nonpublic_schools, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_nearby_hydrants_nps, resource_fire_hydrants, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        
        get_nearby_hydrants_ps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nearby_hydrants_ps, this_script)
        doc.usage(get_nearby_hydrants_ps, resource_public_schools, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_nearby_hydrants_ps, resource_fire_hydrants, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})

        nearby_hydrants_p = doc.entity('dat:npearce#ps_hydrants', {prov.model.PROV_LABEL:'Public Nearby Hydrants', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nearby_hydrants_p, this_script)
        doc.wasGeneratedBy(nearby_hydrants_p, get_nearby_hydrants_ps, endTime)
        doc.wasDerivedFrom(nearby_hydrants_p, resource_public_schools, get_nearby_hydrants_ps, get_nearby_hydrants_ps, get_nearby_hydrants_ps)
        doc.wasDerivedFrom(nearby_hydrants_p, resource_fire_hydrants, get_nearby_hydrants_ps, get_nearby_hydrants_ps, get_nearby_hydrants_ps)
        
        nearby_hydrants_np = doc.entity('dat:npearce#nps_hydrants', {prov.model.PROV_LABEL:'Nonpublic Nearby Hydrants', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nearby_hydrants_np, this_script)
        doc.wasGeneratedBy(nearby_hydrants_np, get_nearby_hydrants_nps, endTime)
        doc.wasDerivedFrom(nearby_hydrants_np, resource_nonpublic_schools, get_nearby_hydrants_nps, get_nearby_hydrants_nps, get_nearby_hydrants_nps)
        doc.wasDerivedFrom(nearby_hydrants_np, resource_fire_hydrants, get_nearby_hydrants_nps, get_nearby_hydrants_nps, get_nearby_hydrants_nps)
        
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
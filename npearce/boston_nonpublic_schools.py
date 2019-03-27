import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class boston_nonpublic_schools(dml.Algorithm):
    contributor = 'npearce'
    reads = []
    writes = ['npearce.boston_nonpublic_schools']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('npearce', 'npearce')

        # Drop and create mongo collection
        repo.dropCollection("boston_nonpublic_schools")
        repo.createCollection("boston_nonpublic_schools")
        
        # API call for fire departments dataset
        url = 'https://opendata.arcgis.com/datasets/0046426a3e4340a6b025ad52b41be70a_1.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        features = json.loads(response)['features']
        
        # Collect point tuples in pts
        pts = []
        for feature in features:
            coords = feature['geometry']['coordinates']
            pt = {'coordinates':coords}
            pts.append(pt)
        repo['npearce.boston_nonpublic_schools'].insert_many(pts)
        
        repo['npearce.boston_nonpublic_schools'].metadata({'complete':True})
        print(repo['npearce.boston_nonpublic_schools'].metadata())
        
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

        this_script = doc.agent('alg:npearce#boston_nonpublic_schools', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:0046426a3e4340a6b025ad52b41be70a_1', {'prov:label':'Non Public Schools', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        get_nps = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nps, this_script)
        doc.usage(get_nps, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Point&$select=coordinates'
                  }
                  )

        nonpublic_schools = doc.entity('dat:npearce#boston_nonpublic_schools', {prov.model.PROV_LABEL:'Non Public Schools', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(nonpublic_schools, this_script)
        doc.wasGeneratedBy(nonpublic_schools, get_nps, endTime)
        doc.wasDerivedFrom(nonpublic_schools, resource, get_nps, get_nps, get_nps)

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
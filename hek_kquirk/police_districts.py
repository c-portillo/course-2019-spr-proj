import geopandas
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import shapefile
import requests
import zipfile
import io

class police_districts(dml.Algorithm):
    contributor = 'hek_kquirk'
    reads = []
    writes = ['hek_kquirk.police_stations']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hek_kquirk', 'hek_kquirk')
        
        l = []
        url = 'https://dataverse.harvard.edu/api/access/datafile/:persistentId/?persistentId=doi:10.7910/DVN/JZV6ON/BGTJS7&version=1.1'
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall() 

        reader = shapefile.Reader("Police_Districts.shp")
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buf = []

        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            geom = sr.shape.__geo_interface__
            buf.append(dict(type="Feature", geometry=geom, properties=atr))
        
        geojson = open("Police_Districts.json", "w")
        geojson.write(json.dumps(buf, sort_keys=True, indent=2) + "\n")
        geojson.close()

        geojson = open("Police_Districts.json", "r")
        repo.dropCollection("police_districts")
        repo.createCollection("police_districts")
        repo['hek_kquirk.police_districts'].insert_many(json.loads(geojson.read()))
        repo['hek_kquirk.police_districts'].metadata({'complete':True})
        print(repo['hek_kquirk.police_districts'].metadata())
        repo.logout()

        endTime = datetime.datetime.now()

        geojson.close()
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
        repo.authenticate('hek_kquirk', 'hek_kquirk')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('dvh', 'https://dataverse.harvard.edu/')

        this_script = doc.agent('alg:hek_kquirk#police_districts', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        resource = doc.entity('dvh:api/access/datafile/:persistentId/', {'prov:label':'Harvard Dataverse', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'zip'})
        police_districts = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(police_districts, this_script)
        doc.usage(police_districts, resource, startTime, None,
                  {
                      prov.model.PROV_TYPE:'ont:Retrieval',
                      'ont:Query':'?persistentId=doi:10.7910/DVN/JZV6ON/BGTJS7&version=1.1'
                  }
        )

        police_districts = doc.entity('dat:hek_kquirk#police_districts', {prov.model.PROV_LABEL:'Boston Police Districts', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(police_districts, this_script)
        doc.wasGeneratedBy(police_districts, police_districts, endTime)
        doc.wasDerivedFrom(police_districts, resource, police_districts, police_districts, police_districts)

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

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class getOil(dml.Algorithm):
    contributor = 'misn15'
    reads = []
    writes = ['misn15.oil']

    @staticmethod
    def execute(trial = False):
        '''Retrieve oil sites data from datamechanics.io'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('misn15', 'misn15')

        url = 'http://datamechanics.io/data/misn15/oil_sites.geojson' 
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("oil")
        repo.createCollection("oil")
        repo['misn15.oil'].insert_many(r['features'])
        repo['misn15.oil'].metadata({'complete':True})
        print(repo['misn15.oil'].metadata())

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
        doc.add_namespace('bdp', 'https://docs.digital.mass.gov/dataset/massgis-data-massdep-tier-classified-oil-andor-hazardous-material-sites-mgl-c-21e')

        this_script = doc.agent('alg:misn15#getOil', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:Boston_oil', {'prov:label':'Boston_oil', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        get_oil = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_oil, this_script)
        doc.usage(get_oil, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        oil = doc.entity('dat:misn15#oil', {prov.model.PROV_LABEL:'Boston Oil', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(oil, this_script)
        doc.wasGeneratedBy(oil, get_oil, endTime)
        doc.wasDerivedFrom(oil, resource, get_oil, get_oil, get_oil)
                  
        return doc

getOil.execute()
doc = getOil.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof

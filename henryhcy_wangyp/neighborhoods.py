import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
#get the data about neighborhoods

class neighborhoods(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = []
    writes = ['henryhcy_wangyp.neighborhoods']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')

       	url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.csv'       
        response = urllib.request.urlopen(url)
        cr = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter = ',')
        # parse the data as following
        rs = []
        i = 0
        for row in cr:
                if(i != 0):
                    dic = {}
                    dic['name'] = row[1]
                    dic['shapeSTArea'] = row[5]
                    dic['shapeSTLength'] = row[6]
                    rs.append(dic)
                i += 1
        repo.dropCollection("neighborhoods")
        repo.createCollection("neighborhoods")
        repo['henryhcy_wangyp.neighborhoods'].insert_many(rs)
        repo['henryhcy_wangyp.neighborhoods'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.neighborhoods'].metadata())
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
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:henryhcy_wangyp#neighborhoods', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:3525b0ee6e6b427f9aab5d0a1d0a1a28_0', {'prov:label':'neighborhoods location', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_neighborhoods = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_neighborhoods, this_script)
        doc.usage(get_neighborhoods, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )
        

        neighborhoods = doc.entity('dat:henryhcy_wangyp#neighborhoods', {prov.model.PROV_LABEL:'neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_neighborhoods, endTime)
        doc.wasDerivedFrom(neighborhoods, resource, get_neighborhoods, get_neighborhoods, get_neighborhoods)

        

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
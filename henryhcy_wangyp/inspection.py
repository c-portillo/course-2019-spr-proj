
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv 
import io
#get the data about neighborhoods

class inspection(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = []
    writes = ['henryhcy_wangyp.inspection']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        url = 'https://data.boston.gov/dataset/03693648-2c62-4a2c-a4ec-48de2ee14e18/resource/4582bec6-2b4f-4f9e-bc55-cbaa73117f4c/download/tmper3diw4s.csv'
        response = urllib.request.urlopen(url)
        cr = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter = ',')
        # parse the data as following
        rs = []
        i = 0
        for row in cr:
                if(i != 0):
                    dic = {}
                    dic['businessName'] = row[0]
                    dic['result'] = row[11]
                    dic['resultdttm'] = row[12]
                    dic['violation_level'] = row[14]
                    dic['viostatus'] = row[17]
                    dic['address'] = row[20]
                    dic['property_id'] = row[24]
                    rs.append(dic)
                i += 1
        repo.dropCollection("inspection")
        repo.createCollection("inspection")
        repo['henryhcy_wangyp.inspection'].insert_many(rs)
        repo['henryhcy_wangyp.inspection'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.inspection'].metadata())
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
        doc.add_namespace('bdp', 'https://data.boston.gov/dataset/')

        this_script = doc.agent('alg:henryhcy_wangyp#inspection', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:03693648-2c62-4a2c-a4ec-48de2ee14e18/resource/4582bec6-2b4f-4f9e-bc55-cbaa73117f4c/download/tmper3diw4s.csv', {'prov:label':'inspection information', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_inspection = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_inspection, this_script)
        doc.usage(get_inspection, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=inspection&$select=businessName,result,resultdttm,viostatus,address,property_id'
                  }
                  )
        

        inspection = doc.entity('dat:henryhcy_wangyp#inspection', {prov.model.PROV_LABEL:'inspection', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(inspection, this_script)
        doc.wasGeneratedBy(inspection, get_inspection, endTime)
        doc.wasDerivedFrom(inspection, resource, get_inspection, get_inspection, get_inspection)

        

        repo.logout()
                  
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
inspection.execute()
doc = inspection.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
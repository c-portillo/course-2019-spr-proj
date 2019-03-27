import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io

class PropertyAssessment(dml.Algorithm):
    contributor = 'ruipang_zhou482'
    reads = []
    writes = ['ruipang_zhou482.PropertyAssessment']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')

        url = 'https://data.boston.gov/dataset/e02c44d2-3c64-459c-8fe2-e1ce5f38a035/resource/fd351943-c2c6-4630-992d-3f895360febd/download/ast2018full.csv'
        response = urllib.request.urlopen(url)
        cr = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter = ',')
        ps =[]
        i =0
        dic={}
        for row in cr:
            if(i != 0):
                # print (row[7])
                if row[7] in dic:
                    # print (row[20])
                    if(row[20]!='' and float(row[20])!=0.0):
                        dic[row[7]][0]+=float(row[18])/float(row[20])
                        dic[row[7]][1]+=1
                    
                else:
                    if(row[20]!='' and float(row[20])!=0.0 and row[7]!=""):
                        p =[]
                        p.append(float(row[18])/float(row[20]))
                        p.append(1)
                        dic[row[7]]=p

            i = i + 1

        for i in dic:
            c = {}
             
            c['zipcode'] = i
            c['avg_value']=dic[i][0]/dic[i][1]
            ps.append(c)
        
        repo.dropCollection("PropertyAssessment")
        repo.createCollection("PropertyAssessment")
        
        
        repo['ruipang_zhou482.PropertyAssessment'].insert_many(ps)
        repo['ruipang_zhou482.PropertyAssessment'].metadata({'complete':True})
        # # print(repo['ruipang_zhou482.PropertyAssessment'].metadata())
        
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
        repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:ruipang_zhou482#PropertyAssessment', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:Boston Property Values',
                              {'prov:label': 'Boston Property Values Data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_propvalue = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_propvalue, this_script)
        doc.usage(get_propvalue, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        propvalue = doc.entity('dat:ruipang_zhou482#propertyvalue', {prov.model.PROV_LABEL:'Boston Property Values ', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(propvalue, this_script)
        doc.wasGeneratedBy(propvalue, get_propvalue, endTime)
        doc.wasDerivedFrom(propvalue, resource, get_propvalue, get_propvalue, get_propvalue)

        repo.logout()

        return doc

PropertyAssessment.execute()
doc = PropertyAssessment.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof

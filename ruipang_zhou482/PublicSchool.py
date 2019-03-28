import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
class PublicSchool(dml.Algorithm):
    contributor = 'ruipang_zhou482'
    reads = []
    writes = ['ruipang_zhou482.PublicSchool']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')
        
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/1d9509a8b2fd485d9ad471ba2fdb1f90_0.csv'
        response = urllib.request.urlopen(url)
        cr = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter = ',')
        ps =[]
        i =0
        dic={}
        for row in cr:
            if(i != 0):
                
                if row[8] in dic:
                    dic[row[8]]+=1
                else:
                    dic[row[8]] =1


            i = i + 1
        # print (dic['02108'])
        for i in dic:
            c = {}
             
            c['zipcode'] = i
            c['num_school']=dic[i]
            ps.append(c)
    
        repo.dropCollection("PublicSchool")
        repo.createCollection("PublicSchool")
        
        
        repo['ruipang_zhou482.PublicSchool'].insert_many(ps)
        repo['ruipang_zhou482.PublicSchool'].metadata({'complete':True})
        
        print(repo['ruipang_zhou482.PublicSchool'].metadata())
        
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

        this_script = doc.agent('alg:ruipang_zhou482#PublicSchool', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:Boston Property Values',
                              {'prov:label': 'Boston Public School Data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_PublicSchool = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_PublicSchool, this_script)
        doc.usage(get_PublicSchool, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        PublicSchool = doc.entity('dat:ruipang_zhou482#PublicSchool', {prov.model.PROV_LABEL:'Boston PublicSchool ', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(PublicSchool, this_script)
        doc.wasGeneratedBy(PublicSchool, get_PublicSchool, endTime)
        doc.wasDerivedFrom(PublicSchool, resource, get_PublicSchool, get_PublicSchool, get_PublicSchool)

        repo.logout()

        return doc

PublicSchool.execute()
doc = PublicSchool.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

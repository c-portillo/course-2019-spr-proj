import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas


class property(dml.Algorithm):
    contributor = 'Jinghang_Yuan'
    reads = []
    writes = ['Jinghang_Yuan.property']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')

        url = 'https://data.boston.gov/dataset/e02c44d2-3c64-459c-8fe2-e1ce5f38a035/resource/fd351943-c2c6-4630-992d-3f895360febd/download/ast2018full.csv'

        df = pandas.read_csv(url)
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)

        repo.dropCollection("property")
        repo.createCollection("property")
        repo['Jinghang_Yuan.property'].insert_many(r)
        repo['Jinghang_Yuan.property'].metadata({'complete': True})

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:Jinghang_Yuan#property',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_property = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_property, this_script)
        doc.usage(get_property, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'PID,CM_ID,GIS_ID,ST_NUM,ST_NAME,ST_NAME_SUF,UNIT_NUM,ZIPCODE,PTYPE,LU,OWN_OCC,OWNER,MAIL_ADDRESSEE,MAIL_ADDRESS,MAIL CS,MAIL_ZIPCODE'
                   }
                  )
        property = doc.entity('dat:Jinghang_Yuan#property',
                          {prov.model.PROV_LABEL: 'property', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(property, this_script)
        doc.wasGeneratedBy(property, get_property, endTime)
        doc.wasDerivedFrom(resource, property, get_property, get_property, get_property)

        repo.logout()

        return doc
property.execute()
# doc = property.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

##eof

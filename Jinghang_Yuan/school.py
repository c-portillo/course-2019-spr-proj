import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas

class school(dml.Algorithm):
    contributor = 'Jinghang_Yuan'
    reads = []
    writes = ['Jinghang_Yuan.school']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')

        url = 'https://opendata.arcgis.com/datasets/0046426a3e4340a6b025ad52b41be70a_1.csv'
        df = pandas.read_csv(url)
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)

        repo.dropCollection("school")
        repo.createCollection("school")
        repo['Jinghang_Yuan.school'].insert_many(r)
        repo['Jinghang_Yuan.school'].metadata({'complete': True})
        # print('-----------------')
        # print(list(repo['Jinghang_Yuan.school'].find()))
        # print('-----------------')

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

        this_script = doc.agent('alg:Jinghang_Yuan#school',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_school = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_school, this_script)
        doc.usage(get_school, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'X,Y,OBJECTID_1,OBJECTID,SCHID,NAME,ADDRESS,TOWN_MAIL,TOWN,STATE,ZIP,PRINCIPAL,PHONE,FAX,GRADES,TYPE'
                   }
                  )
        school = doc.entity('dat:Jinghang_Yuan#school',
                          {prov.model.PROV_LABEL: 'school', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(school, this_script)
        doc.wasGeneratedBy(school, get_school, endTime)
        doc.wasDerivedFrom(resource, school, get_school, get_school, get_school)

        repo.logout()

        return doc
school.execute()
# doc = school.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

##eof

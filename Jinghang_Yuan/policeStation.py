import urllib.request
import json
import dml
import prov.model
import datetime
import uuid



class policeStation(dml.Algorithm):
    contributor = 'Jinghang_Yuan'
    reads = []
    writes = ['Jinghang_Yuan.policeStation']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')

        url = 'http://datamechanics.io/data/Jinghang_Yuan/policeStation.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("policeStation")
        repo.createCollection("policeStation")
        repo['Jinghang_Yuan.policeStation'].insert_many(r)
        repo['Jinghang_Yuan.policeStation'].metadata({'complete': True})
        # print('-----------------')
        # print(list(repo['Jinghang_Yuan.policeStation'].find()))
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

        this_script = doc.agent('alg:Jinghang_Yuan#policeStation',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_policeStation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_policeStation, this_script)
        doc.usage(get_policeStation, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'OBJECTID,BLDG_ID,BID,ADDRESS,POINT_X,POINT_Y,NAME,NEIGHBOTHOOD,CITY,ZIP,FT_SOFT,STORY_HT,PARCEL_ID'
                   }
                  )
        policeStation = doc.entity('dat:Jinghang_Yuan#policeStation',
                          {prov.model.PROV_LABEL: 'policeStation', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(policeStation, this_script)
        doc.wasGeneratedBy(policeStation, get_policeStation, endTime)
        doc.wasDerivedFrom(resource, policeStation, get_policeStation, get_policeStation, get_policeStation)

        repo.logout()

        return doc
policeStation.execute()
# doc = property.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

##eof

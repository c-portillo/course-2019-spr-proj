import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class getLinkedin(dml.Algorithm):
    contributor = 'emmaliu_yuyangl'
    reads = []
    writes = ['emmaliu_gaotian_xli33_yuyangl.linkedin']


    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('emmaliu_gaotian_xli33_yuyangl', 'emmaliu_gaotian_xli33_yuyangl')

        url = 'http://datamechanics.io/data/linkedindataset.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("linkedin")
        repo.createCollection("linkedin")
        repo['emmaliu_gaotian_xli33_yuyangl.linkedin'].insert_many(r)
        repo['emmaliu_gaotian_xli33_yuyangl.linkedin'].metadata({'complete': True})
        print(repo['emmaliu_gaotian_xli33_yuyangl.linkedin'].metadata())

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}



    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo

        repo.authenticate('emmaliu_gaotian_xli33_yuyangl', 'emmaliu_gaotian_xli33_yuyangl')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/emmaliu_gaotian_xli33_yuyangl')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/emmaliu_gaotian_xli33_yuyangl')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', '')

        this_script = doc.agent('alg:emmaliu_gaotian_xli33_yuyangl#getLinkedin',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:linkedinapi',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_Linkedin = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_Linkedin, this_script)
        doc.usage(get_Linkedin, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                    }
                  )

        Linkedin = doc.entity('dat:emmaliu_gaotian_xli33_yuyangl#get_linkedin',
                          {prov.model.PROV_LABEL: 'linkedin', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(Linkedin, this_script)
        doc.wasGeneratedBy(Linkedin, get_Linkedin, endTime)
        doc.wasDerivedFrom(Linkedin, resource, get_Linkedin, get_Linkedin, get_Linkedin)

        repo.logout()

        return doc


# getLinkedin.execute()
# doc = getLinkedin.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof

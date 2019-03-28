import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class edu_job(dml.Algorithm):
    contributor = 'ojhamb_runtongy_sgullett_zybu'
    reads = []
    writes = ['ojhamb_runtongy_sgullett_zybu.edu_job']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')

        url = 'http://datamechanics.io/data/amman_eco_job.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)

        repo.dropCollection("edu_job")
        repo.createCollection("edu_job")
        repo['ojhamb_runtongy_sgullett_zybu.edu_job'].insert_many(r)
        repo['ojhamb_runtongy_sgullett_zybu.edu_job'].metadata({'complete': True})
        print(repo['ojhamb_runtongy_sgullett_zybu.edu_job'].metadata())

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
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        # doc.add_namespace('bdp', 'http://www.dos.gov.jo/dos_home_a/main/population/census2015/WorkForce/')

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu#edu_job',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('dat:amman_eco_job',
                              {'prov:label': 'Economic Activity Status', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        '''
        resource = doc.entity('bdp:WorkingForce_5.12.pdf',
                              {'prov:label': 'Economic Activity Status', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'pdf'})
        '''
        get_Econ_Status = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_Econ_Status, this_script)
        doc.usage(get_Econ_Status, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        Econ_Status = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#edu_job',
                          {prov.model.PROV_LABEL: 'Econ_Status', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(Econ_Status, this_script)
        doc.wasGeneratedBy(Econ_Status, get_Econ_Status, endTime)
        doc.wasDerivedFrom(Econ_Status, resource, get_Econ_Status, get_Econ_Status, get_Econ_Status)

        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
edu_job.execute()
doc = edu_job.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
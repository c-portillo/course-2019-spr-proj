import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class age_cur_edu(dml.Algorithm):
    contributor = 'ojhamb_runtongy_sgullett_zybu'
    reads = []
    writes = ['ojhamb_runtongy_sgullett_zybu.age_cur_edu']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')

        url = 'http://datamechanics.io/data/amman_edu_age.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)

        repo.dropCollection("age_cur_edu")
        repo.createCollection("age_cur_edu")
        repo['ojhamb_runtongy_sgullett_zybu.age_cur_edu'].insert_many(r)
        repo['ojhamb_runtongy_sgullett_zybu.age_cur_edu'].metadata({'complete': True})
        print(repo['ojhamb_runtongy_sgullett_zybu.age_cur_edu'].metadata())

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
        # doc.add_namespace('bdp', 'http://www.dos.gov.jo/dos_home_a/main/population/census2015/Education/')

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu#age_cur_edu',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('dat:amman_edu_age',
                              {'prov:label': 'Educational Stage', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        '''
        resource = doc.entity('bdp:Education_4.3.pdf',
                              {'prov:label': 'Educational Stage', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'pdf'})
        '''
        get_Edu_Stage = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_Edu_Stage, this_script)
        doc.usage(get_Edu_Stage, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        Edu_Stage = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#age_cur_edu',
                          {prov.model.PROV_LABEL: 'Edu_Stage', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(Edu_Stage, this_script)
        doc.wasGeneratedBy(Edu_Stage, get_Edu_Stage, endTime)
        doc.wasDerivedFrom(Edu_Stage, resource, get_Edu_Stage, get_Edu_Stage, get_Edu_Stage)

        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
age_cur_edu.execute()
doc = age_cur_edu.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
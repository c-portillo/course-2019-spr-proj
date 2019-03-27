import json
import dml
import prov.model
import datetime
import uuid
import math

class edu_work(dml.Algorithm):
    contributor = 'ojhamb_runtongy_sgullett_zybu'
    reads = ['ojhamb_runtongy_sgullett_zybu.age_cur_edu', 'ojhamb_runtongy_sgullett_zybu.edu_job']
    writes = ['ojhamb_runtongy_sgullett_zybu.edu_work']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')

        repo.dropCollection("edu_work")
        repo.createCollection("edu_work")

        # Do projection to the original dataset to get the rate of employment of each educational attainment
        edu_eco = [(x["Educational Attainment"], x["Employed"]/x["Total"])
                   for x in repo.ojhamb_runtongy_sgullett_zybu.edu_job.find()]

        # Do selection to get only the data related to Higher educational attainment
        high_edu = [x for x in edu_eco if x[0] in ["Bachelor", "Higher Diploma", "Master", "PhD"]]

        # Do projection to the original dataset to get only the number of people
        # belong to a specific age group of each education stage
        edu_age = [(x["Education Stage"], x["19-23"]+x["24-29"])
                   for x in repo.ojhamb_runtongy_sgullett_zybu.age_cur_edu.find()]

        # Do selection to get only the data related to Higher educational attainment
        high_edu_age = [x for x in edu_age if x[0] in ["Bachelor", "Higher Diploma", "Master", "PhD"]]

        # Do product to the two data sets
        high_group_dup = [(x, y) for x in high_edu for y in high_edu_age]

        # Do projection to eliminate the duplicate and get the result that
        # how many people will get hired in each degree based on the employment rate in the past
        high_group = [(edu1, math.floor(pop*rate)) for ((edu1, pop), (edu2, rate)) in high_group_dup if edu1==edu2]

        edu_work = []

        for x in high_group:
            edu_work.append({"Educational Attainment": x[0], "Number of Expected Employment": x[1]})

        repo['ojhamb_runtongy_sgullett_zybu.edu_work'].insert_many(edu_work)
        repo['ojhamb_runtongy_sgullett_zybu.edu_work'].metadata({'complete': True})
        print(repo['ojhamb_runtongy_sgullett_zybu.edu_work'].metadata())

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

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu#edu_work',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        edu_job = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#edu_job',
                              {'prov:label': 'Educational Attainment and Employment', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        age_cur_edu = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#age_cur_edu',
                              {'prov:label': 'Age and Current Education Stage', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_edu_work = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_edu_work, this_script)

        doc.usage(get_edu_work, edu_job, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_edu_work, age_cur_edu, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        edu_work = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#edu_work',
                          {prov.model.PROV_LABEL: 'Future Employment', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(edu_work, this_script)
        doc.wasGeneratedBy(edu_work, get_edu_work, endTime)
        doc.wasDerivedFrom(edu_work, edu_job, get_edu_work, get_edu_work, get_edu_work)
        doc.wasDerivedFrom(edu_work, age_cur_edu, get_edu_work, get_edu_work, get_edu_work)

        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
edu_work.execute()
doc = edu_work.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
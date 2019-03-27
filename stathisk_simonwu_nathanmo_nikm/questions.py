import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as koalas


class questions(dml.Algorithm):
    contributor = 'stathisk_simonwu_nathanmo_nikm'
    reads = []
    writes = ['stathisk_simonwu_nathanmo_nikm.q1', 'stathisk_simonwu_nathanmo_nikm.q2', 'stathisk_simonwu_nathanmo_nikm.q3', 'stathisk_simonwu_nathanmo_nikm.q4']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        dml.pymongo.MongoClient()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')

        urls = ['http://electionstats.state.ma.us/ballot_questions/download/7295/precincts_include:1/',
                'http://electionstats.state.ma.us/ballot_questions/download/7294/precincts_include:1/',
                'http://electionstats.state.ma.us/ballot_questions/download/7296/precincts_include:1/',
                'http://electionstats.state.ma.us/ballot_questions/download/7297/precincts_include:1/']

        for i in range(0, len(urls)):
            question = "q" + str(i + 1)
            repo.dropCollection(question)
            repo.createCollection(question)

            df = koalas.read_csv(urls[i])
            collection = 'stathisk_simonwu_nathanmo_nikm.' + question
            repo[collection].insert_many(json.loads(df.to_json(orient='records')))
            repo[collection].metadata({'complete': True})

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
        # return doc
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('ballotquestions', 'http://electionstats.state.ma.us/ballot_questions/')

        this_script = doc.agent('alg:stathisk_simonwu_nathanmo_nikm#questions',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource1 = doc.entity('dat:question1',
                               {'prov:label': 'ballot question1 answers ', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        resource2 = doc.entity('dat:question2',
                               {'prov:label': 'ballot question2 answers', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extensio': 'json'})
        resource3 = doc.entity('dat:question3',
                               {'prov:label': 'ballot question3 answers', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        resource4 = doc.entity('dat:question4',
                               {'prov:label': 'ballot question4 answers', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})

        get_q1 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_q2 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_q3 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_q4 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_q1, this_script)
        doc.wasAssociatedWith(get_q2, this_script)
        doc.wasAssociatedWith(get_q3, this_script)
        doc.wasAssociatedWith(get_q4, this_script)

        doc.usage(get_q1, resource1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        doc.usage(get_q1, resource2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_q1, resource3, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_q1, resource4, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        q1 = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#q1',
                        {prov.model.PROV_LABEL: 'Question1', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(q1, this_script)
        doc.wasGeneratedBy(q1, get_q1, endTime)
        doc.wasDerivedFrom(q1, resource1, get_q1, get_q1, get_q1)

        q2 = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#q2',
                        {prov.model.PROV_LABEL: 'Question2', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(q2, this_script)
        doc.wasGeneratedBy(q2, get_q2, endTime)
        doc.wasDerivedFrom(q2, resource2, get_q2, get_q2, get_q2)

        q3 = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#q3',
                        {prov.model.PROV_LABEL: 'Question3', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(q3, this_script)
        doc.wasGeneratedBy(q3, get_q3, endTime)
        doc.wasDerivedFrom(q3, resource3, get_q3, get_q3, get_q3)

        q4 = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#q4',
                        {prov.model.PROV_LABEL: 'Question4', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(q4, this_script)
        doc.wasGeneratedBy(q4, get_q4, endTime)
        doc.wasDerivedFrom(q4, resource4, get_q4, get_q4, get_q4)

        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

questions.execute(True)
doc = questions.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

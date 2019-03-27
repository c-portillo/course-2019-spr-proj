"""
CS504 : ballotQuestionsResults
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : retrieval of ballot question voter results

Notes :

February 26, 2019
"""

import csv
import datetime
import io
import json
import uuid

import dml
import prov.model
import urllib.request

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, BALLOT_QUESTIONS_RESULTS, BALLOT_QUESTIONS_NAME, BALLOT_QUESTIONS_RESULTS_NAME, BALLOT_QUESTION_DOWNLOAD_RESULTS_URL


class ballotQuestionsResults(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [BALLOT_QUESTIONS_NAME]
    writes = [BALLOT_QUESTIONS_RESULTS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Retrieve ballot question results data from electionstats and insert into collection
            ex) {
                    "Locality" : "Bourne",
                    "Ward" : "-",
                    "Pct" : "7",
                    "Yes" : 375,
                    "No" : 914,
                    "Blanks" : 26,
                    "Total Votes Cast" : 1315,
                    "Question ID" : "7303"
                }
        """

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get list of question ids from collection
        questionsIds = list(repo[BALLOT_QUESTIONS_NAME].find({}, {"_id":1}))
        questionResultsRows = []

        # Use question ids to retrieve data from electionstats for each ballot question
        for question in questionsIds:
            id = question['_id']
            url = BALLOT_QUESTION_DOWNLOAD_RESULTS_URL.format(id=id)
            csvString = urllib.request.urlopen(url).read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(csvString))
            data = json.loads(json.dumps(list(reader)))
            data = [ballotQuestionsResults.cleanData(row, id) for row in data]
            questionResultsRows.extend(data)

        # Insert rows into collection
        repo.dropCollection(BALLOT_QUESTIONS_RESULTS)
        repo.createCollection(BALLOT_QUESTIONS_RESULTS)
        repo[BALLOT_QUESTIONS_RESULTS_NAME].insert_many(questionResultsRows)
        repo[BALLOT_QUESTIONS_RESULTS_NAME].metadata({'complete': True})
        print(repo[BALLOT_QUESTIONS_RESULTS_NAME].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def cleanData(precinctDictionary, id):
        """ Add Question ID field, change num votes values to int"""

        # Add ID field
        precinctDictionary['Question ID'] = id

        # Convert Yes, No, Blanks, Total Votes Values to integers
        precinctDictionary['Yes'] = int(precinctDictionary['Yes'].replace(',',''))
        precinctDictionary['No'] = int(precinctDictionary['No'].replace(',',''))
        precinctDictionary['Blanks'] = int(precinctDictionary['Blanks'].replace(',',''))
        precinctDictionary['Total Votes Cast'] = int(precinctDictionary['Total Votes Cast'].replace(',',''))

        return precinctDictionary


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
        repo.authenticate(TEAM_NAME, TEAM_NAME)
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('electionstats', 'http://electionstats.state.ma.us/')

        this_script = doc.agent('alg:'+TEAM_NAME+'#ballotQuestionsResults', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('electionstats:ballot_questions/download/', {'prov:label': 'PD43+: Election Stats Ballot Questions', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        ballotQuestionsEntity = doc.entity('dat:' + TEAM_NAME + '#ballotQuestions', {prov.model.PROV_LABEL: 'Ballot Questions', prov.model.PROV_TYPE: 'ont:DataSet'})
        get_ballotQuestionsResults = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_ballotQuestionsResults, this_script)
        doc.usage(get_ballotQuestionsResults, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': '{id}/precincts_include:1/'})
        doc.usage(get_ballotQuestionsResults, ballotQuestionsEntity, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'question ID'})

        ballotQuestionsResultsEntity = doc.entity('dat:'+TEAM_NAME+'#ballotQuestionsResults', {prov.model.PROV_LABEL: 'MA Ballot Questions Results 2000-2018',prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(ballotQuestionsResultsEntity, this_script)
        doc.wasGeneratedBy(ballotQuestionsResultsEntity, get_ballotQuestionsResults, endTime)
        doc.wasDerivedFrom(ballotQuestionsResultsEntity, resource, get_ballotQuestionsResults, get_ballotQuestionsResults, get_ballotQuestionsResults)
        doc.wasDerivedFrom(ballotQuestionsResultsEntity, ballotQuestionsEntity, get_ballotQuestionsResults, get_ballotQuestionsResults, get_ballotQuestionsResults)

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
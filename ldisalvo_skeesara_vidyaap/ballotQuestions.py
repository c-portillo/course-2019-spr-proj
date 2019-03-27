"""
CS504 : ballotQuestions
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : retrieval of ballot question metadata

Notes :

February 27, 2019
"""

import datetime
import uuid

import dml
import prov.model

from bs4 import BeautifulSoup
from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, BALLOT_QUESTIONS, BALLOT_QUESTIONS_NAME, BALLOT_QUESTION_2000_2018_URL
from ldisalvo_skeesara_vidyaap.helper.scraper import scraper

class ballotQuestions(dml.Algorithm):
    contributor = TEAM_NAME
    reads = []
    writes = [BALLOT_QUESTIONS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Scrape electionstats to get data about each MA ballot question (2000-2018)
            and insert into collection
            ex) {
                    "_id" : "7322",
                    "year" : 2018,
                    "number" : "4",
                    "description" : "SUMMARY Sections 3 to 7 of Chapter 44B of the General Laws
                        of Massachusetts, also known as the Community Preservation Act (the 'Act'),
                        establishes a dedicated funding source for the: acquisition, creation and
                        preservation of open space; acquisition, preservation, rehabilitation and
                        restoration of hi...",
                    "type" : "Local Question",
                    "location" : "Various cities/towns"
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get HTML of page and pull all ballot question divs
        raw_html = scraper.simple_get(BALLOT_QUESTION_2000_2018_URL)
        html = BeautifulSoup(raw_html, 'html.parser')
        questionList = html.findAll("tr", {"class": "election_item"})

        ballotQuestionsRows = []

        # Build row for each ballot questions
        for question in questionList:
            questionData = {}
            questionData['_id'] = question['id'].split('-')[-1]
            questionData['year'] = int(question.findAll("td", {"class": "year"})[0].contents[0])
            questionData['number'] = question.findAll("td", {"class": "number"})[0].contents[0]
            questionData['description'] = question.findAll("td", {"class": "display_question"})[0].contents[0]
            questionData['type'] = question.findAll("td", {"class": "bq_types"})[0].contents[0] \
                if question.findAll("td", {"class": "bq_types"})[0].contents \
                else ''
            questionData['location'] = question.findAll("td", {"class": "bq_location"})[0].contents[0]
            ballotQuestionsRows.append(questionData)

        # Insert rows into collection
        repo.dropCollection(BALLOT_QUESTIONS)
        repo.createCollection(BALLOT_QUESTIONS)
        repo[BALLOT_QUESTIONS_NAME].insert_many(ballotQuestionsRows)
        repo[BALLOT_QUESTIONS_NAME].metadata({'complete': True})
        print(repo[BALLOT_QUESTIONS_NAME].metadata())

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
        repo.authenticate(TEAM_NAME, TEAM_NAME)
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('electionstats', 'http://electionstats.state.ma.us/')

        this_script = doc.agent('alg:'+TEAM_NAME+'#ballotQuestions', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('electionstats:ballot_questions/search/', {'prov:label': 'PD43+: Election Stats', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'html'})
        get_ballotQuestions = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_ballotQuestions, this_script)
        doc.usage(get_ballotQuestions, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'year_from:2000/year_to:2018'})

        ballotQuestionsEntity = doc.entity('dat:'+TEAM_NAME+'#ballotQuestions', {prov.model.PROV_LABEL: 'MA Ballot Questions 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(ballotQuestionsEntity, this_script)
        doc.wasGeneratedBy(ballotQuestionsEntity, get_ballotQuestions, endTime)
        doc.wasDerivedFrom(ballotQuestionsEntity, resource, get_ballotQuestions, get_ballotQuestions, get_ballotQuestions)

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
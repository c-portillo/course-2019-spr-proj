"""
CS504 : stateSenateElections
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : retrieval of state senate election metadata

Notes : 

February 27, 2019
"""

import datetime
import uuid

import dml
import prov.model

from bs4 import BeautifulSoup
from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_SENATE_ELECTIONS, STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_GENERAL_2000_2018_URL
from ldisalvo_skeesara_vidyaap.helper.scraper import scraper


class stateSenateElections(dml.Algorithm):
    contributor = TEAM_NAME
    reads = []
    writes = [STATE_SENATE_ELECTIONS_NAME]


    @staticmethod
    def execute(trial=False):
        """
            Scrape electionstats to get data about each MA general state senate election (2000-2018)
            and insert into collection
            ex) {
                    "_id" : "131666",
                    "year" : 2018,
                    "district" : "1st Middlesex",
                    "candidates" :
                    [ {
                        "name" : "Edward J. Kennedy",
                        "party" : "Democratic",
                        "isWinner" : true
                    }, {
                        "name" : "John A. Macdonald",
                        "party" : "Republican",
                        "isWinner" : false
                    } ] }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get HTML of page and pull all election divs
        raw_html = scraper.simple_get(STATE_SENATE_GENERAL_2000_2018_URL)
        html = BeautifulSoup(raw_html, 'html.parser')
        electionsList = html.findAll("tr", {"class": "election_item"})

        electionsRows = []

        # Build row for each election
        for election in electionsList:
            electionData = {}
            electionData['_id'] = election['id'].split('-')[-1]
            electionData['year'] = int(election.findAll("td", {"class": "year"})[0].contents[0])
            electionData['district'] = election.findAll("td", {"class": ""})[1].contents[0]

            # Build sub json for candidates containing name, party, and isWinner
            electionData['candidates'] = []
            table = election.find("table", {"class": "candidates"})

            winner = table.find("tr", {"class": "is_winner"}).find("td", {"class": "candidate"})
            electionData['candidates'].append(stateSenateElections.buildCandidateRow(winner, True))

            otherCandidates = table.findAll("td", {"class": "candidate"})[1:]
            [electionData['candidates'].append(stateSenateElections.buildCandidateRow(candidate, False)) for candidate in otherCandidates]
            electionData['candidates'] = [x for x in electionData['candidates'] if x is not None]

            electionsRows.append(electionData)

        # Insert rows into collection
        repo.dropCollection("stateSenateElection")
        repo.dropCollection(STATE_SENATE_ELECTIONS)
        repo.createCollection(STATE_SENATE_ELECTIONS)
        repo[STATE_SENATE_ELECTIONS_NAME].insert_many(electionsRows)
        repo[STATE_SENATE_ELECTIONS_NAME].metadata({'complete': True})
        print(repo[STATE_SENATE_ELECTIONS_NAME].metadata())

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

        this_script = doc.agent('alg:' + TEAM_NAME + '#stateSenateElections', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('electionstats:elections/search/', {'prov:label': 'PD43+: Election Stats', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'html'})
        get_stateSenateElections = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stateSenateElections, this_script)
        doc.usage(get_stateSenateElections, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'year_from:2000/year_to:2018/office_id:9/stage:General'})

        stateSenateElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElections', {prov.model.PROV_LABEL: 'MA General State Senate Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(stateSenateElectionsEntity, this_script)
        doc.wasGeneratedBy(stateSenateElectionsEntity, get_stateSenateElections, endTime)
        doc.wasDerivedFrom(stateSenateElectionsEntity, resource, get_stateSenateElections, get_stateSenateElections, get_stateSenateElections)

        repo.logout()

        return doc


    def buildCandidateRow(candidateDiv, isWinner):
        if not candidateDiv.find("div"):
            return

        candidateData = {}
        candidateData['name'] = candidateDiv.find("div", {"class": "name"}).find("a").contents[0]
        candidateData['party'] = candidateDiv.find("div", {"class": "party"}).contents[0] \
            if candidateDiv.find("div", {"class": "party"}).contents \
            else ''
        candidateData['isWinner'] = isWinner
        return candidateData


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
## eof
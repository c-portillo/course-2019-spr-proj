"""
CS504 : stateSenateElectionsResults
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : retrieval of state senate election voter results

Notes :

February 26, 2019
"""

import csv
import datetime
import io
import json
import uuid

import urllib.request
import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_SENATE_ELECTIONS_RESULTS, STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME, ELECTION_DOWNLOAD_RESULTS_URL

class stateSenateElectionsResults(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_SENATE_ELECTIONS_NAME]
    writes = [STATE_SENATE_ELECTIONS_RESULTS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Retrieve election results data from electionstats and insert into collection
            ex) {
                    "City/Town" : "Egremont",
                    "Ward" : "-",
                    "Pct" : "1",
                    "Election ID" : "131526",
                    "Adam G Hinds" : 682,
                    "All Others" : 0,
                    "Blanks" : 111,
                    "Total Votes Cast" : 793
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get list of election ids from collection
        electionIds = list(repo[STATE_SENATE_ELECTIONS_NAME].find({}, {"_id":1}))
        electionResultsRows = []

        # Use election ids to retrieve data from electionstats for each state senate election
        for question in electionIds:
            id = question['_id']
            url = ELECTION_DOWNLOAD_RESULTS_URL.format(id=id)
            csvString = urllib.request.urlopen(url).read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(csvString))
            data = json.loads(json.dumps(list(reader)))
            data = [stateSenateElectionsResults.cleanData(row, id) for row in data[1:]]
            electionResultsRows.extend(data)

        # Insert rows into collection
        repo.dropCollection(STATE_SENATE_ELECTIONS_RESULTS)
        repo.createCollection(STATE_SENATE_ELECTIONS_RESULTS)
        repo[STATE_SENATE_ELECTIONS_RESULTS_NAME].insert_many(electionResultsRows)
        repo[STATE_SENATE_ELECTIONS_RESULTS_NAME].metadata({'complete': True})
        print(repo[STATE_SENATE_ELECTIONS_RESULTS_NAME].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def cleanData(precinctDictionary, id):
        """ Add Election ID field, change num votes values to int, remove '.' from middle initial"""

        # Add ID field
        precinctDictionary['Election ID'] = id

        keysToChange = list(precinctDictionary.keys())[3:-1]
        for key in keysToChange:
            precinctDictionary[key] = int(precinctDictionary[key].replace(',',''))
            precinctDictionary[key.replace('.','')] = precinctDictionary.pop(key)

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

        this_script = doc.agent('alg:' + TEAM_NAME + '#stateSenateElectionsResults', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('electionstats:elections/download/', {'prov:label': 'PD43+: Election Stats State Senate Elections', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        stateSenateElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElections', {prov.model.PROV_LABEL: 'MA General State Senate Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        get_stateSenateElectionsResults = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stateSenateElectionsResults, this_script)
        doc.usage(get_stateSenateElectionsResults, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': '{id}/precincts_include:1/'})
        doc.usage(get_stateSenateElectionsResults, stateSenateElectionsEntity, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'Election ID'})

        stateSenateElectionsResultsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElectionsResults', {prov.model.PROV_LABEL: 'MA General State Senate Elections Results 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(stateSenateElectionsResultsEntity, this_script)
        doc.wasGeneratedBy(stateSenateElectionsResultsEntity, get_stateSenateElectionsResults, endTime)
        doc.wasDerivedFrom(stateSenateElectionsResultsEntity, resource, get_stateSenateElectionsResults, get_stateSenateElectionsResults, get_stateSenateElectionsResults)
        doc.wasDerivedFrom(stateSenateElectionsResultsEntity, stateSenateElectionsEntity, get_stateSenateElectionsResults, get_stateSenateElectionsResults, get_stateSenateElectionsResults)

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
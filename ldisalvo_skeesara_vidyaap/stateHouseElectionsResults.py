"""
CS504 : stateHouseElectionsResults
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : retrieval of state house election voter results

Notes : 

February 28, 2019
"""

import csv
import datetime
import io
import json
import uuid

import dml
import prov.model
import urllib.request

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_HOUSE_ELECTIONS_RESULTS, STATE_HOUSE_ELECTIONS_NAME, STATE_HOUSE_ELECTIONS_RESULTS_NAME, ELECTION_DOWNLOAD_RESULTS_URL


class stateHouseElectionsResults(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_HOUSE_ELECTIONS_NAME]
    writes = [STATE_HOUSE_ELECTIONS_RESULTS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Retrieve election results data from electionstats and insert into collection
            ex) {
                    "City/Town" : "Barnstable",
                    "Ward" : "-",
                    "Pct" : "7",
                    "Election ID" : "131582",
                    "William L Crocker, Jr" : 1079,
                    "Paul J Cusack" : 1059,
                    "All Others" : 5,
                    "Blanks" : 42,
                    "Total Votes Cast" : 2185
                }
        """

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get list of election ids from collection
        electionIds = list(repo[STATE_HOUSE_ELECTIONS_NAME].find({}, {"_id":1}))
        electionResultsRows = []

        # Use election ids to retrieve data from electionstats for each state house election
        for question in electionIds:
            id = question['_id']
            url = ELECTION_DOWNLOAD_RESULTS_URL.format(id=id)
            csvString = urllib.request.urlopen(url).read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(csvString))
            data = json.loads(json.dumps(list(reader)))
            data = [stateHouseElectionsResults.cleanData(row, id) for row in data[1:]]
            electionResultsRows.extend(data)

        # Insert rows into collection
        repo.dropCollection(STATE_HOUSE_ELECTIONS_RESULTS)
        repo.createCollection(STATE_HOUSE_ELECTIONS_RESULTS)
        repo[STATE_HOUSE_ELECTIONS_RESULTS_NAME].insert_many(electionResultsRows)
        repo[STATE_HOUSE_ELECTIONS_RESULTS_NAME].metadata({'complete': True})
        print(repo[STATE_HOUSE_ELECTIONS_RESULTS_NAME].metadata())

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
        doc.add_namespace('electionstats','http://electionstats.state.ma.us/')

        this_script = doc.agent('alg:'+TEAM_NAME+'#stateHouseElectionsResults', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('electionstats:elections/download/', {'prov:label': 'PD43+: Election Stats State House Elections',prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        stateHouseElectionsEntity = doc.entity('dat:'+TEAM_NAME+'#stateHouseElections', {prov.model.PROV_LABEL: 'MA General State House Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        get_stateHouseElectionsResults = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stateHouseElectionsResults, this_script)
        doc.usage(get_stateHouseElectionsResults, resource, startTime, None,{prov.model.PROV_TYPE: 'ont:Retrieval','ont:Query': '{id}/precincts_include:1/'})
        doc.usage(get_stateHouseElectionsResults, stateHouseElectionsEntity, startTime, None,{prov.model.PROV_TYPE: 'ont:Retrieval','ont:Query': 'Election ID'})

        stateHouseElectionsResultsEntity = doc.entity('dat:'+TEAM_NAME+'#stateHouseElectionsResults', {prov.model.PROV_LABEL: 'MA General State House Elections Results 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(stateHouseElectionsResultsEntity, this_script)
        doc.wasGeneratedBy(stateHouseElectionsResultsEntity, get_stateHouseElectionsResults, endTime)
        doc.wasDerivedFrom(stateHouseElectionsResultsEntity, resource, get_stateHouseElectionsResults, get_stateHouseElectionsResults, get_stateHouseElectionsResults)
        doc.wasDerivedFrom(stateHouseElectionsResultsEntity, stateHouseElectionsEntity, get_stateHouseElectionsResults, get_stateHouseElectionsResults, get_stateHouseElectionsResults)

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
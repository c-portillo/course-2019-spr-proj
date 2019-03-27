"""
CS504 : transformationSenateDistrictIdeology
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : transformation of state senate election data to determine basic ideology of each senate district

Notes:

March 01, 2019
"""

import datetime
import uuid

import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_SENATE_ELECTIONS_NAME, SENATE_DISTRICT_IDEOLOGIES, SENATE_DISTRICT_IDEOLOGIES_NAME

class transformationSenateDistrictIdeology(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_SENATE_ELECTIONS_NAME]
    writes = [SENATE_DISTRICT_IDEOLOGIES_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Transformation to determine basic ideology score for each house district by calculating
            number of republican or democratic candidates elected from each district from 2000-2018
            ex) {
                    "district" : "1st Hampden and Hampshire",
                    "percentDem" : 70,
                    "percentRepub" : 30,
                    "numDemWins" : 7,
                    "numRepubWins" : 3,
                    "numElections" : 10
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get list of distinct state senate districts
        districtList = list(repo[STATE_SENATE_ELECTIONS_NAME].distinct("district"))
        districtRows = []

        # For each district, find number of democratic and republican wins for every election from 2000-2018
        for district in districtList:
            districtData = {}
            elections = list(repo[STATE_SENATE_ELECTIONS_NAME].find({"district": district}))
            numDemWins, numRepubWins = transformationSenateDistrictIdeology.countPartyWins(elections)
            numElections = len(elections)

            districtData["district"] = district
            districtData["percentDem"] = numDemWins/numElections * 100
            districtData["percentRepub"] = numRepubWins/numElections * 100
            districtData["numDemWins"] = numDemWins
            districtData["numRepubWins"] = numRepubWins
            districtData["numElections"] = numElections
            districtRows.append(districtData)

        # Insert rows into collection
        repo.dropCollection(SENATE_DISTRICT_IDEOLOGIES)
        repo.createCollection(SENATE_DISTRICT_IDEOLOGIES)
        repo[SENATE_DISTRICT_IDEOLOGIES_NAME].insert_many(districtRows)
        repo[SENATE_DISTRICT_IDEOLOGIES_NAME].metadata({'complete': True})
        print(repo[SENATE_DISTRICT_IDEOLOGIES_NAME].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def countPartyWins(electionsList):
        """ Return number of democratic and republican wins within a list of elections"""
        numDemWins = 0
        numRepubWins = 0

        for election in electionsList:
            candidatesList = election['candidates']
            for candidate in candidatesList:
                if candidate['isWinner']:
                    if candidate['party'] == 'Democratic': numDemWins += 1
                    elif candidate['party'] == 'Republican': numRepubWins += 1

        return numDemWins, numRepubWins

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

        this_script = doc.agent('alg:' + TEAM_NAME + '#transformationSenateDistrictIdeology', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        stateSenateElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElections', {prov.model.PROV_LABEL: 'MA General State Senate Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_transformationSenateDistrictIdeology = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transformationSenateDistrictIdeology, this_script)
        doc.usage(get_transformationSenateDistrictIdeology, stateSenateElectionsEntity, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'distinct district name'})

        transformationSenateDistrictIdeologyEntity = doc.entity('dat:' + TEAM_NAME + '#transformationSenateDistrictIdeology', {prov.model.PROV_LABEL: 'Basic MA State Senate District Ideology Score 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(transformationSenateDistrictIdeologyEntity, this_script)
        doc.wasGeneratedBy(transformationSenateDistrictIdeologyEntity, get_transformationSenateDistrictIdeology, endTime)
        doc.wasDerivedFrom(transformationSenateDistrictIdeologyEntity, stateSenateElectionsEntity, get_transformationSenateDistrictIdeology, get_transformationSenateDistrictIdeology, get_transformationSenateDistrictIdeology)

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
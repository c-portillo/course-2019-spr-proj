"""
CS504 : transformationHouseDistrictIdeology
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : transformation of state house election data to determine basic ideology of each house district

Notes:

March 01, 2019
"""

import datetime
import uuid

import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_HOUSE_ELECTIONS_NAME, HOUSE_DISTRICT_IDEOLOGIES, HOUSE_DISTRICT_IDEOLOGIES_NAME

class transformationHouseDistrictIdeology(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_HOUSE_ELECTIONS_NAME]
    writes = [HOUSE_DISTRICT_IDEOLOGIES_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Transformation to determine basic ideology score for each house district by calculating
            number of republican or democratic candidates elected from each district from 2000-2018
            ex) {
                    "district" : "1st Barnstable",
                    "percentDem" : 25,
                    "percentRepub" : 75,
                    "numDemWins" : 1,
                    "numRepubWins" : 3,
                    "numElections" : 4
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get list of distinct state house districts
        districtList = list(repo[STATE_HOUSE_ELECTIONS_NAME].distinct("district"))
        districtRows = []

        # For each district, find number of democratic and republican wins for every election from 2000-2018
        for district in districtList:
            districtData = {}
            elections = list(repo[STATE_HOUSE_ELECTIONS_NAME].find({"district": district}))
            numDemWins, numRepubWins = transformationHouseDistrictIdeology.countPartyWins(elections)
            numElections = len(elections)

            districtData["district"] = district
            districtData["percentDem"] = numDemWins/numElections * 100
            districtData["percentRepub"] = numRepubWins/numElections * 100
            districtData["numDemWins"] = numDemWins
            districtData["numRepubWins"] = numRepubWins
            districtData["numElections"] = numElections
            districtRows.append(districtData)

        # Insert rows into collection
        repo.dropCollection(HOUSE_DISTRICT_IDEOLOGIES)
        repo.createCollection(HOUSE_DISTRICT_IDEOLOGIES)
        repo[HOUSE_DISTRICT_IDEOLOGIES_NAME].insert_many(districtRows)
        repo[HOUSE_DISTRICT_IDEOLOGIES_NAME].metadata({'complete': True})
        print(repo[HOUSE_DISTRICT_IDEOLOGIES_NAME].metadata())

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

        this_script = doc.agent('alg:'+TEAM_NAME+'#transformationHouseDistrictIdeology', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        stateHouseElectionsEntity = doc.entity('dat:'+TEAM_NAME+'#stateHouseElections', {prov.model.PROV_LABEL: 'MA General State House Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_transformationHouseDistrictIdeology = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transformationHouseDistrictIdeology, this_script)
        doc.usage(get_transformationHouseDistrictIdeology, stateHouseElectionsEntity, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'distinct district name'})

        transformationHouseDistrictIdeologyEntity = doc.entity('dat:'+TEAM_NAME+'#transformationHouseDistrictIdeology', {prov.model.PROV_LABEL: 'Basic MA State House District Ideology Score 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(transformationHouseDistrictIdeologyEntity, this_script)
        doc.wasGeneratedBy(transformationHouseDistrictIdeologyEntity, get_transformationHouseDistrictIdeology, endTime)
        doc.wasDerivedFrom(transformationHouseDistrictIdeologyEntity, stateHouseElectionsEntity, get_transformationHouseDistrictIdeology, get_transformationHouseDistrictIdeology, get_transformationHouseDistrictIdeology)

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
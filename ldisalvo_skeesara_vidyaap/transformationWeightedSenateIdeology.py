"""
CS504 : demographicData.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : Transformation of data to create weighted ideology scores for each senate district

Notes:

February 28, 2019
"""

import datetime
import uuid

import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME, WEIGHTED_SENATE_IDEOLOGIES_NAME, WEIGHTED_SENATE_IDEOLOGIES


class transformationWeightedSenateIdeology(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME]
    writes = [WEIGHTED_SENATE_IDEOLOGIES_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Read from State Senate Elections and Results tables to create a weighted average of Democratic,
            Republican, other, and blank votes over time and insert into collection
            ex) {
                    "district" : "1st Hampden and Hampshire",
                    "Democratic ratio" : .6,
                    "Republican ratio" : .2,
                    "Others ratio" : .1,
                    "Blanks ratios" : .1,
                    "Totals" : 1
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)


        electionsByDistrict = list(repo[STATE_SENATE_ELECTIONS_NAME].find({}))
        finalAvgsByDistrict = {}


        for tup in electionsByDistrict:
            # find the results row with the district totals
            totalRow = list(repo[STATE_SENATE_ELECTIONS_RESULTS_NAME].find(
                {"City/Town":"TOTALS",
                 "Election ID":tup["_id"]
                 }))[0]


            # find which candidate was the Democrat and which was the Republican
            dem = ""
            rep = ""
            others = []

            for c in tup["candidates"]:
                candidate = c["party"]
                if candidate == "Democratic":
                    dem = c["name"].replace('.','')
                elif candidate == "Republican":
                    rep = c["name"].replace('.','')
                else:
                    others += [c["name"].replace('.', '')]

            # find the ratio of votes that each candidate got

            total_count = totalRow["Total Votes Cast"]
            dem_ratio = 0
            rep_ratio = 0
            others_count = 0

            for o in others:
                if o != "":
                    try:
                        others_count += totalRow[o]
                    except KeyError:
                        print("Note: Unable to find 'other' candidate: ", o)

            others_ratio = float(others_count/total_count)
            blanks_ratio = float(totalRow["Blanks"]/total_count)

            if dem != "":
                try:
                    dem_ratio = float(totalRow[dem]/total_count)
                except KeyError as e:
                    print("NOTE: Democrat not located: ", dem)


            if rep != "":
                try:
                    rep_ratio = float(totalRow[rep]/total_count)
                except KeyError:
                    print("NOTE: Republic not location: ", rep)


            if tup["district"] in finalAvgsByDistrict:
                finalAvgsByDistrict[tup["district"]] += [(dem_ratio, rep_ratio, others_ratio, blanks_ratio)]
            else:
                finalAvgsByDistrict[tup["district"]] = [(dem_ratio, rep_ratio, others_ratio, blanks_ratio)]

        # calculate the average over time (using helper) and insert into database
        new_list = []
        for k, v in finalAvgsByDistrict.items():
            avg_tup = transformationWeightedSenateIdeology.tuple_avg(v)
            new_json = {}
            new_json["district"] = k
            new_json["Democratic ratio"] = avg_tup[0]
            new_json["Republican ratio"] = avg_tup[1]
            new_json["Others ratio"] = avg_tup[2]
            new_json["Blanks ratio"] = avg_tup[3]
            new_json["Total"] = avg_tup[4]
            new_list += [new_json]


        repo.dropCollection(WEIGHTED_SENATE_IDEOLOGIES)
        repo.createCollection(WEIGHTED_SENATE_IDEOLOGIES_NAME)
        repo[WEIGHTED_SENATE_IDEOLOGIES_NAME].insert_many(new_list)
        repo[WEIGHTED_SENATE_IDEOLOGIES_NAME].metadata({'complete': True})
        print(repo[WEIGHTED_SENATE_IDEOLOGIES_NAME].metadata())


        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def tuple_avg(tupList):

        # print("tupList = ", tupList)

        count = 0
        tupSum = [0]*len(tupList[0])

        for tup in tupList:
            count += 1
            for i in range(len(tup)):
                tupSum[i] += tup[i]

        # print("tupSum = ", tupSum)

        tupAvg = [0]*len(tupSum)

        for i in range(len(tupSum)):
            tupAvg[i] = tupSum[i]/count

        total = sum(tupAvg)
        tupAvg += [total]

        return tupAvg

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
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:ldisalvo_skeesara_vidyaap#transformationWeightedSenateIdeology',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        stateSenateElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElections',
                                               {prov.model.PROV_LABEL: 'MA General State Senate Elections 2000-2018',
                                                prov.model.PROV_TYPE: 'ont:DataSet'})
        stateSenateElectionsResultsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElectionsResults', {
            prov.model.PROV_LABEL: 'MA General State Senate Elections Results 2000-2018',
            prov.model.PROV_TYPE: 'ont:DataSet'})

        get_weighted_senate_ideology = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_weighted_senate_ideology, this_script)

        doc.usage(get_weighted_senate_ideology, stateSenateElectionsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Name'
                   }
                  )
        doc.usage(get_weighted_senate_ideology, stateSenateElectionsResultsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Election ID'
                   }
                  )

        weighted_senate_ideology = doc.entity('dat:ldisalvo_skeesara_vidyaap#transformationWeightedSenateIdeology',
                                       {prov.model.PROV_LABEL: 'Weighted Ideologies of Senate Elections',
                                        prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(weighted_senate_ideology, this_script)
        doc.wasGeneratedBy(weighted_senate_ideology, get_weighted_senate_ideology, endTime)
        doc.wasDerivedFrom(weighted_senate_ideology, stateSenateElectionsEntity, get_weighted_senate_ideology, get_weighted_senate_ideology,
                           get_weighted_senate_ideology)
        doc.wasDerivedFrom(weighted_senate_ideology, stateSenateElectionsResultsEntity, get_weighted_senate_ideology,
                           get_weighted_senate_ideology, get_weighted_senate_ideology)

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
"""
CS504 : demographicData.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : Transformation of data to generate summary statistics on demographic information

Notes:

February 28, 2019
"""

import datetime
import uuid

import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME,DEMOGRAPHIC_DATA_COUNTY_NAME, DEMOGRAPHIC_DATA_TOWN_NAME, \
    SUMMARY_DEMOGRAPHICS_METRICS_NAME, SUMMARY_DEMOGRAPHICS_METRICS


class transformationSummaryMetrics(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [DEMOGRAPHIC_DATA_COUNTY_NAME, DEMOGRAPHIC_DATA_TOWN_NAME]
    writes = [SUMMARY_DEMOGRAPHICS_METRICS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Retrieve summary demographic data for all facts by county and town and insert into collection
            ex)
                {'Fact': 'Population estimates, July 1, 2017,  (V2017)',
                'Town_Min': 'Middleton town, Essex County, Massachusetts',
                'Town_Min_Val': '9,861',
                'Town_Max': 'Littleton town, Middlesex County, Massachusetts',
                'Town_Max_Value': '10,115',
                'County_Min': 'Worcester County, Massachusetts',
                'County_Min_Val': '826,116',
                'County_Max': 'Middlesex County, Massachusetts',
                'County_Max_Value': '1,602,947'}

        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Retrieve facts as keys
        document = repo[DEMOGRAPHIC_DATA_COUNTY_NAME].find_one()
        keys = []
        for key in document:
            keys += [key]

        # Remove Fact, Town, and FIPS keys
        keys = keys[2:-1]

        # Initialize collection
        repo.dropCollection(SUMMARY_DEMOGRAPHICS_METRICS)
        repo.createCollection(SUMMARY_DEMOGRAPHICS_METRICS)

        # Iterate through key facts finding the min and max values among towns and counties
        for x in keys:
            queryMaxTown = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({x : {"$ne": float('nan')}}, {"Town": 1, x: 1}).sort(x, -1).limit(1))
            queryMinTown = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({x : {"$ne": float('nan')}}, {"Town": 1, x: 1}).sort(x, 1).limit(1))

            queryMaxCounty = list(repo[DEMOGRAPHIC_DATA_COUNTY_NAME].find({x : {"$ne": float('nan')}}, {"County": 1, x: 1}).sort(x, -1).limit(1))
            queryMinCounty = list(repo[DEMOGRAPHIC_DATA_COUNTY_NAME].find({x : {"$ne": float('nan')}}, {"County": 1, x: 1}).sort(x, 1).limit(1))

            try:
                queryInsert = {"Fact":x, "Town_Min" : queryMinTown[0]["Town"], "Town_Min_Val": queryMinTown[0][x],
                               "Town_Max": queryMaxTown[0]["Town"], "Town_Max_Value": queryMaxTown[0][x],
                               "County_Min" : queryMinCounty[0]["County"], "County_Min_Val": queryMinCounty[0][x],
                               "County_Max": queryMaxCounty[0]["County"], "County_Max_Value": queryMaxCounty[0][x]}

                repo[SUMMARY_DEMOGRAPHICS_METRICS_NAME].insert_one(queryInsert)

            except:
                continue

        repo[SUMMARY_DEMOGRAPHICS_METRICS_NAME].metadata({'complete': True})
        print(repo[SUMMARY_DEMOGRAPHICS_METRICS_NAME].metadata())

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
        doc.add_namespace('alg',
                          'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat',
                          'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:'+TEAM_NAME+ '#transformationSummaryMetrics',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'],
                                 'ont:Extension': 'py'})

        demographicDataCountyEntity = doc.entity('dat:'+TEAM_NAME+'#demographicDataCounty', {prov.model.PROV_LABEL: 'Census Data by County, Massachusetts',
                                                 prov.model.PROV_TYPE: 'ont:DataSet'})

        demographicDataTownEntity = doc.entity('dat:' + TEAM_NAME + '#demographicDataTown',
                                                 {prov.model.PROV_LABEL: 'Census Data by Town, Massachusetts',
                                                  prov.model.PROV_TYPE: 'ont:DataSet'})

        get_transformationSummaryMetrics = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transformationSummaryMetrics, this_script)
        doc.usage(get_transformationSummaryMetrics, demographicDataCountyEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   }
                  )
        doc.usage(get_transformationSummaryMetrics, demographicDataTownEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   }
                  )

        transformationSummaryMetricsEntity = doc.entity('dat:' +TEAM_NAME+'#transformationSummaryMetrics', {prov.model.PROV_LABEL: 'Max and min metrics by town and county',
                                                 prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(transformationSummaryMetricsEntity, this_script)
        doc.wasGeneratedBy(transformationSummaryMetricsEntity, get_transformationSummaryMetrics, endTime)
        doc.wasDerivedFrom(transformationSummaryMetricsEntity, demographicDataCountyEntity, get_transformationSummaryMetrics, get_transformationSummaryMetrics, get_transformationSummaryMetrics)
        doc.wasDerivedFrom(transformationSummaryMetricsEntity, demographicDataTownEntity, get_transformationSummaryMetrics, get_transformationSummaryMetrics, get_transformationSummaryMetrics)

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





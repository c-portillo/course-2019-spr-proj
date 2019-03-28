import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from collections import Counter
import csv
import io
from urllib.request import urlopen


class EffectOfRoadConditions(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = ['darren68_gladding_ralcalde.Revere2016']
    writes = ['darren68_gladding_ralcalde.RoadConditionsEffectRevere2016']


    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')



        newDataSet = []

        collection = repo.darren68_gladding_ralcalde.Revere2016

        roadConditions = EffectOfRoadConditions.getDistinctConditions(collection)

        for condition in roadConditions:
            newDoc = {}
            mannersOfCollision= EffectOfRoadConditions.\
                selectOnRoadConditionandProjectMannerOfCollision(collection,condition)
            aggregatedData = EffectOfRoadConditions.aggregate(mannersOfCollision)
            newDoc[condition] = aggregatedData
            newDataSet.append(newDoc)

        repo.dropCollection("RoadConditionsEffectRevere2016")
        repo.createCollection("RoadConditionsEffectRevere2016")
        repo["darren68_gladding_ralcalde.RoadConditionsEffectRevere2016"].insert_many(newDataSet)
        repo["darren68_gladding_ralcalde.RoadConditionsEffectRevere2016"].metadata({'complete': True})
        repo.logout()


        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}


    @staticmethod
    def aggregate(collisions):
        mannerOfCollisionWithCount = dict(Counter(collisions))
        return mannerOfCollisionWithCount


    @staticmethod
    def selectOnRoadConditionandProjectMannerOfCollision(collection, condition):
        mannersOfCollision = []
        for doc in collection.find():
            if doc['roadsurfacecondition'] == condition:
                mannersOfCollision.append(doc['mannerofcollision'])
        return mannersOfCollision


    @staticmethod
    def getDistinctConditions(collection):
        conditions = []
        for doc in collection.find():
            conditions.append(doc['roadsurfacecondition'])
        return list(set(conditions))



    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.


        # Agent, entity, activity
        this_script = doc.agent('alg:darren68_gladding_ralcalde#EffectOfRoadConditions',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})


        Revere2016_data = doc.entity('dat:darren68_gladding_ralcalde#Revere2016',
                              {'prov:label': 'Revere 2016 data', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})

        # Activity
        get_Revere2016Data = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_Revere2016Data, this_script)

        doc.usage(get_Revere2016Data, Revere2016_data, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   })


        EffectOfConditions = doc.entity('dat:darren68_gladding_ralcalde#RoadConditionsEffectRevere2016',
                             {prov.model.PROV_LABEL: "Effect of Revere's Road Conditions"
                                 , prov.model.PROV_TYPE: 'ont:DataSet'})
        createEffectData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(createEffectData, this_script)
        doc.wasAttributedTo(EffectOfConditions, this_script)
        doc.wasGeneratedBy(EffectOfConditions, createEffectData, endTime)
        doc.usage(createEffectData, Revere2016_data, startTime, None,
                  {prov.model.PROV_LABEL: "Effect of Revere's Road Conditions"
                      , prov.model.PROV_TYPE: 'ont:Computation'})
        doc.wasDerivedFrom(EffectOfConditions, Revere2016_data, createEffectData, createEffectData, createEffectData)

        repo.logout()

        return doc



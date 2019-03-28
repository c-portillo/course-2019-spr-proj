import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
from urllib.request import urlopen
from statistics import mean


class RateofChange2010To2016(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = ['darren68_gladding_ralcalde.AllTowns1990to2016']
    writes = ['darren68_gladding_ralcalde.AllTownsRateofChange2010To2016']


    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')

        newDataSet = []

        collection = repo.darren68_gladding_ralcalde.AllTowns1990to2016

        rates = []
        for doc in collection.find():
            if doc['Town'] == "TOTAL":
                 continue
            newDoc = {
                'Town' : doc['Town'],
                '2010' : doc['2010'],
                '2016' : doc['2016']
            }
            change = RateofChange2010To2016.calcChange(int(newDoc['2010']), int(newDoc['2016']))

            if not isinstance(change, str):
                rates.append(change)
                newDoc['% Change 2010-2016'] = RateofChange2010To2016.formatRate(change)
            else:
                newDoc['% Change 2010-2016'] = change

            newDataSet.append(newDoc)

        averageChangeRate = RateofChange2010To2016.formatRate(mean(rates))

        for doc in newDataSet:
            doc['Average % Change 2010-2016'] = averageChangeRate

        repo.dropCollection("AllTownsRateofChange2010To2016")
        repo.createCollection("AllTownsRateofChange2010To2016")
        repo['darren68_gladding_ralcalde.AllTownsRateofChange2010To2016'].insert_many(newDataSet)
        repo['darren68_gladding_ralcalde.AllTownsRateofChange2010To2016'].metadata({'complete': True})

        repo.logout()
        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}



    @staticmethod
    def formatRate(r):
        rate = str(r*100).split('.')

        if len(rate[1]) == 1:
            return rate[0] + '.' + rate[1] + '0%'
        else:
            return rate[0] + '.' + rate[1][0:2] + '%'




    @staticmethod
    def calcChange(_2010, _2016):
        if _2010 != 0:
            changeRate = (_2016 - _2010) / _2010
        else:
            changeRate = "N/A"
        return changeRate






    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.


        # Agent, entity, activity
        this_script = doc.agent('alg:darren68_gladding_ralcalde#RateofChange2010To2016',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})


        AllTowns_data = doc.entity('dat:darren68_gladding_ralcalde#AllTowns1990to2016',
                              {'prov:label': "All Towns' Accident Data 1990-2016", prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'csv'})


        # Activity
        get_TownData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_TownData, this_script)

        doc.usage(get_TownData, AllTowns_data, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   })

        RateofChangeDataSet = doc.entity('dat:darren68_gladding_ralcalde#AllTownsRateofChange2010To2016',
                             {prov.model.PROV_LABEL: "Shows Rate of Change in Accidents from 2010 to 2016"
                                 , prov.model.PROV_TYPE: 'ont:DataSet'})

        createRoCData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(createRoCData, this_script)
        doc.wasAttributedTo(RateofChangeDataSet, this_script)
        doc.wasGeneratedBy(RateofChangeDataSet, createRoCData, endTime)
        doc.usage(createRoCData, AllTowns_data, startTime, None,
                  {prov.model.PROV_LABEL: "Used accident data from all the towns to compute rates of change in accidents"
                      , prov.model.PROV_TYPE: 'ont:Computation'})


        doc.wasDerivedFrom(RateofChangeDataSet, AllTowns_data, createRoCData, createRoCData, createRoCData)
        repo.logout()

        return doc




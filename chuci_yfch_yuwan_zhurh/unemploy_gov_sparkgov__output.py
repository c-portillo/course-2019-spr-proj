#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class unemploy_gov_sparkgov__output(dml.Algorithm):
    contributor = 'chuci_yfch_yuwan_zhurh'
    reads = ['chuci_yfch_yuwan_zhurh.unemploy', 'chuci_yfch_yuwan_zhurh.gov', 'chuci_yfch_yuwan_zhurh.sparkgov']
    writes = ['chuci_yfch_yuwan_zhurh.spark2018govdata', 'chuci_yfch_yuwan_zhurh.city_unemploy_baker']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        def select(R, s):
            return [t for t in R if s(t)]
        def product(R, S):
            return [(t,u) for t in R for u in S]
        def project(R, p):
            return [p(t) for t in R]


        #select project unemploy and gov dataset to produce a new dataset
        unemploy= repo['chuci_yfch_yuwan_zhurh.unemploy']
        gov=repo['chuci_yfch_yuwan_zhurh.gov']

        y1=list(unemploy.find({},{'City':1,'Rate % Dec-18':1}))
        y2=list(gov.find({'party':'GOP'},{'reportingunitname':1,'votepct':1}))
        x=select(product(y1,y2), lambda t: t[0]['City'] == t[1]['reportingunitname'])
        yyy=project(x,lambda t:{'City':t[0]['City'],'unemploy_rate':t[0]['Rate % Dec-18'],'Baker_selection_rate':t[1]['votepct']})
        repo.dropCollection("city_unemploy_baker")
        repo.createCollection("city_unemploy_baker")
        repo["chuci_yfch_yuwan_zhurh.city_unemploy_baker"].insert_many(yyy)
                                
        #project sparkgov dataset
       # spark=repo['chuci_yfch_yuwan_zhurh.sparkgov']

        pipline = [
            {'$group': {'_id': "$Party ", 'number': {'$sum': 1}}}
           ]
        agg_result = repo['chuci_yfch_yuwan_zhurh.sparkgov'].aggregate(pipline)
        agg_list = list(agg_result)
        repo.dropCollection("spark2018govdata")
        repo.createCollection("spark2018govdata")
        repo["chuci_yfch_yuwan_zhurh.spark2018govdata"].insert_many(agg_list)
        # xx=list(spark.find({"Year": 2018}))
        # repo.dropCollection("spark2018govdata")
        # repo.createCollection("spark2018govdata")
        
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
        # New
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        
        agent = doc.agent('alg:chuci_yfch_yuwan_zhurh#unemploy_gov_sparkgov__output',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        entity_unemploy = doc.entity('dat:chuci_yfch_yuwan_zhurh#unemploy',
                           {prov.model.PROV_LABEL: 'unemploy data', prov.model.PROV_TYPE: 'ont:DataSet'})
        entity_gov = doc.entity('dat:chuci_yfch_yuwan_zhurh#gov',
                           {prov.model.PROV_LABEL: 'gov data', prov.model.PROV_TYPE: 'ont:DataSet'})
        entity_sparkgov = doc.entity('dat:chuci_yfch_yuwan_zhurh#sparkgov',
                           {prov.model.PROV_LABEL: 'sparkgov data', prov.model.PROV_TYPE: 'ont:DataSet'})
        entity_spark2018govdata_result = doc.entity('dat:chuci_yfch_yuwan_zhurh#spark2018govdata_result',
                                   {prov.model.PROV_LABEL: 'spark2018govdata_result data', prov.model.PROV_TYPE: 'ont:DataSet'})
        entity_city_unemploy_baker_result = doc.entity('dat:chuci_yfch_yuwan_zhurh#city_unemploy_baker_result',
                                   {prov.model.PROV_LABEL: 'city_unemploy_baker_result data', prov.model.PROV_TYPE: 'ont:DataSet'})
       
        activity = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
       
        doc.wasAssociatedWith(activity, agent)
        doc.usage(activity, entity_unemploy, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:product select and project'}
                  )
        doc.usage(activity, entity_gov, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:product select and project'}
                  )
        doc.usage(activity, entity_sparkgov, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:select and aggregate'}
                  )
        doc.wasDerivedFrom(entity_city_unemploy_baker_result, entity_unemploy, activity, activity, activity)
        doc.wasDerivedFrom(entity_city_unemploy_baker_result, entity_gov, activity, activity, activity)
        doc.wasDerivedFrom(entity_spark2018govdata_result, entity_sparkgov, activity, activity, activity)
        doc.wasAttributedTo(entity_spark2018govdata_result, agent)
        doc.wasAttributedTo(entity_city_unemploy_baker_result, agent)
        doc.wasGeneratedBy(entity_city_unemploy_baker_result, activity, endTime)
        doc.wasGeneratedBy(entity_spark2018govdata_result, activity, endTime)
        repo.logout()

        return doc


#!/usr/bin/env python
# coding: utf-8

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class join_by_ZIP(dml.Algorithm):
    contributor = 'Jinghang_Yuan'
    reads = ['Jinghang_Yuan.center', 'Jinghang_Yuan.centerPool', 'Jinghang_Yuan.policeStation','Jinghang_Yuan.school','Jinghang_Yuan.property']
    writes = ['Jinghang_Yuan.countAll']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')
        def count(R,key):
            c = 0
            for r in R:
                if(r['ZIP']==key):
                    c += 1
            return c


        r_center= repo['Jinghang_Yuan.center']
        r_centerPool=repo['Jinghang_Yuan.centerPool']
        r_policeStation = repo['Jinghang_Yuan.policeStation']
        r_property = repo['Jinghang_Yuan.property']
        r_school = repo['Jinghang_Yuan.school']

        center=list(r_center.find({},{'_id':0,'ZIP':1,}))
        centerPool=list(r_centerPool.find({},{'_id':0,'ZIP':1}))
        policeStation = list(r_policeStation.find({},{'_id':0,'ZIP':1}))
        property = list(r_property.find({},{'_id':0,'ZIPCODE':1,'AV_TOTAL':1,'GROSS_AREA':1}))
        school = list(r_school.find({},{'_id':0,'ZIP':1}))
        #print(center)
        val_dic = {}
        ar_dic = {}
        ppty_avg = {}
        #print(property[0])
        for ppty in property:
            #val_dic.setdefault(ppty['ZIPCODE'],0)
            if(ppty['GROSS_AREA'] is not None):
                if(val_dic.__contains__(str(ppty['ZIPCODE'])[:-2])):
                    val_dic[str(ppty['ZIPCODE'])[:-2]]+=ppty['AV_TOTAL']
                    #print(ppty['GROSS_AREA'])
                    ar_dic[str(ppty['ZIPCODE'])[:-2]]+=ppty['GROSS_AREA']
                else:
                    val_dic[str(ppty['ZIPCODE'])[:-2]]=ppty['AV_TOTAL']
                    ar_dic[str(ppty['ZIPCODE'])[:-2]]=ppty['GROSS_AREA']
        #print(val_dic)

        for k in val_dic:
            if(ar_dic[k]!=0):
                ppty_avg[k] = val_dic[k]/ar_dic[k]
        #print(ppty_avg)

        res = []
        for key in ppty_avg:
            res.append({'ZIP':key,'val_avg':ppty_avg[key]})
        #print(res)
        for r in res:
            r['centerNum']=count(center,r['ZIP'])
            r['centerPoolNum'] = count(centerPool,r['ZIP'])
            r['policeStationNum'] = count(policeStation,r['ZIP'])
            r['schoolNum'] = count(school,r['ZIP'])
        print(res)

        repo.dropCollection("ZIPCounter")
        repo.createCollection("ZIPCounter")
        repo["Jinghang_Yuan.ZIPCounter"].insert_many(res)
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
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        agent = doc.agent('alg:Jinghang_Yuan#count_all_by_zip',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
     
        property = doc.entity('dat:Jinghang_Yuan#property',
                           {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        school = doc.entity('dat:Jinghang_Yuan#school',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        center = doc.entity('dat:Jinghang_Yuan#center',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        centerPool = doc.entity('dat:Jinghang_Yuan#centerPool',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        policeStation = doc.entity('dat:Jinghang_Yuan#policeStation',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        count_all_by_zip = doc.entity('dat:Jinghang_Yuan#count_all_by_zip',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        activity = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(activity, agent)

        doc.usage(activity, property, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:product select and project'}
                  )
        doc.usage(activity, school, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:product select and project'}
                  )
        doc.usage(activity, centerPool, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:select and aggregate'}
                  )
        doc.usage(activity, center, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:select and aggregate'}
                  )
        doc.usage(activity, policeStation, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:select and aggregate'}
                  )
        doc.wasDerivedFrom(school, count_all_by_zip, activity, activity, activity)
        doc.wasDerivedFrom(centerPool, count_all_by_zip, activity, activity, activity)
        doc.wasDerivedFrom(center, count_all_by_zip, activity, activity, activity)
        doc.wasDerivedFrom(policeStation, count_all_by_zip, activity, activity, activity)
        doc.wasDerivedFrom(property, count_all_by_zip, activity, activity, activity)
        doc.wasAttributedTo(count_all_by_zip, agent)
        doc.wasGeneratedBy(count_all_by_zip, activity, endTime)
        
        repo.logout()

        return doc

join_by_ZIP.execute()

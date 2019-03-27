import dml
from pymongo import MongoClient
import bson.code
import requests 
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import prov.model
import uuid

# Sorts the districts by average class size.
# Then sorts the districts that offer / do not offer grades 9-12 by average class size.

class categorize_class_sizes(dml.Algorithm):
    contributor = 'emilymo'
    reads = ['d.distr', 'd.size']
    writes = ['d.distr3', 'd.djoin1', 'd.djoin2', 'd.sizecategories', 'd.sizecategorieshs']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        client = dml.pymongo.MongoClient() # TO FIX: AUTH??
        d = client.d
    
        for nm in d['distr'].find():
            d['distr3'].insert_one({'district':nm['value']['district']})
            
        for i in d['size'].find():
            for j in d['distr3'].find():
                if i['District Name'] == j['district']:
                    d['djoin1'].insert_one({'district':j['district'], 'avgsize':i['Average Class Size'], 'districtcode':i['District Code']})
                    
        for i in d['djoin1'].find():
            for j in d['grade'].find():
                if i['districtcode'] == j['value']['districtcode']:
                    d['djoin2'].insert_one({'district':j['value']['district'], 'districtcode':i['districtcode'], 
                                         'avgsize':i['avgsize'], 'gradelist':j['value']['gradelist'], 'hs':j['value']['h']})
    
        mapsize = bson.code.Code("""
            function () {     
                if (this['avgsize'] < 10) {
                    sizecat = 'Less than 10'
                }
                else if (this['avgsize'] >= 10 & this['avgsize'] < 20) {
                    sizecat = '10 - 19'
                }
                else if (this['avgsize'] >= 20 & this['avgsize'] < 30) {
                    sizecat = '20 - 29'
                }
                else if (this['avgsize'] >= 30) {
                    sizecat = '30 and above'
                }
                    
                emit(sizecat, {'count':1})
            }
            """)
        redsize = bson.code.Code("""
            function (k, vs) {    
                var sum = 0;
                
                vs.forEach(function(v) {
                  sum += v['count'];
                })
            return {'count':sum}
            }
            """)
        d['djoin2'].map_reduce(mapsize, redsize, 'sizecategories')
        
        mapsize2 = bson.code.Code("""
            function () {     
                if (this['avgsize'] < 10 & this['hs'] == 1) {
                    sizecat = 'Offers High School, Avg. Class Size Less than 10'
                }
                else if (this['avgsize'] >= 10 & this['avgsize'] < 20 & this['hs'] == 1) {
                    sizecat = 'Offers High School, Avg. Class Size 10 - 19'
                }
                else if (this['avgsize'] >= 20 & this['avgsize'] < 30 & this['hs'] == 1) {
                    sizecat = 'Offers High School, Avg. Class Size 20 - 29'
                }
                else if (this['avgsize'] >= 30 & this['hs'] == 1) {
                    sizecat = 'Offers High School, Avg. Class Size 30 and above'
                }
                
                else if (this['avgsize'] < 10 & this['hs'] == 0) {
                    sizecat = 'Does Not Offer High School, Avg. Class Size Less than 10'
                }
                else if (this['avgsize'] >= 10 & this['avgsize'] < 20 & this['hs'] == 0) {
                    sizecat = 'Does Not Offer High School, Avg. Class Size 10 - 19'
                }
                else if (this['avgsize'] >= 20 & this['avgsize'] < 30 & this['hs'] == 0) {
                    sizecat = 'Does Not Offer High School, Avg. Class Size 20 - 29'
                }
                else if (this['avgsize'] >= 30 & this['hs'] == 0) {
                    sizecat = 'Does Not Offer High School, Avg. Class Size 30 and above'
                }
                    
                emit(sizecat, {'count':1})
            }
            """)
        redsize2 = bson.code.Code("""
            function (k, vs) {    
                var sum = 0;
                
                vs.forEach(function(v) {
                  sum += v['count'];
                })
            return {'count':sum}
            }
            """)
        d['djoin2'].map_reduce(mapsize2, redsize2, 'sizecategorieshs')
        
        d.logout()
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}
    
    
    
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/') 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        
        this_script = doc.agent('alg:emilymo#categorize_class_sizes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent']})
        categorize_class_sizes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        distr = doc.entity('dat:emilymo#distr', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts', prov.model.PROV_TYPE:'ont:DataSet'})
        size = doc.entity('dat:emilymo#size', {prov.model.PROV_LABEL:'Massachusetts Class Sizes by District', prov.model.PROV_TYPE:'ont:DataSet'})
        distr3 = doc.entity('dat:emilymo#distr3', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School District Names', prov.model.PROV_TYPE:'ont:DataSet'})
        djoin1 = doc.entity('dat:emilymo#djoin1', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts with Class Sizes', prov.model.PROV_TYPE:'ont:DataSet'})
        djoin2 = doc.entity('dat:emilymo#djoin2', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts with Class Sizes and High School Status', prov.model.PROV_TYPE:'ont:DataSet'})
        sizecategories = doc.entity('dat:emilymo#sizecategories', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts Categorized by Average Class Size', prov.model.PROV_TYPE:'ont:DataSet'})
        sizecategorieshs = doc.entity('dat:emilymo#sizecategorieshs', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts Categorized by Average Class Size and High School Status', prov.model.PROV_TYPE:'ont:DataSet'})
        
        doc.wasAssociatedWith(categorize_class_sizes, this_script)
        doc.used(distr, this_script, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(distr3, this_script, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(djoin1, this_script, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(djoin2, this_script, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(size, this_script, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasDerivedFrom(distr3, distr)
        doc.wasDerivedFrom(djoin1, distr3)
        doc.wasDerivedFrom(djoin1, size)
        doc.wasDerivedFrom(djoin2, djoin1)
        doc.wasDerivedFrom(sizecategories, djoin2)
        doc.wasDerivedFrom(sizecategorieshs, djoin2)
        doc.wasAttributedTo(distr3, this_script)
        doc.wasAttributedTo(djoin1, this_script)
        doc.wasAttributedTo(djoin2, this_script)
        doc.wasAttributedTo(sizecategories, this_script)
        doc.wasAttributedTo(sizecategorieshs, this_script)
        doc.wasGeneratedBy(distr3, categorize_class_sizes)
        doc.wasGeneratedBy(djoin1, categorize_class_sizes)
        doc.wasGeneratedBy(djoin2, categorize_class_sizes)
        doc.wasGeneratedBy(sizecategories, categorize_class_sizes)
        doc.wasGeneratedBy(sizecategorieshs, categorize_class_sizes)
        
        
        return doc
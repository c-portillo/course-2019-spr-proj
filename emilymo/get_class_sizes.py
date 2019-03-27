import dml
from pymongo import MongoClient
import bson.code
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import prov.model
import uuid

# Retrieves information on average class sizes in school districts in Massachusetts.

class get_class_sizes(dml.Algorithm):
    contributor = 'emilymo'
    reads = []
    writes = ['d.size']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        client = dml.pymongo.MongoClient() # TO FIX: AUTH??
        d = client.d
        
        site = 'http://profiles.doe.mass.edu/statereport/classsizebyraceethnicity.aspx'
        pg = requests.get(site)
        sp = bs(pg.content, "lxml")
        tbl = sp.find('table')
        rows = tbl.find_all('tr')
        l = []
        for tr in rows: 
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            l.append(row)
        colnamesraw = [str(c.string) for c in sp.find_all('th')]
        colnames = [name.replace(' %', '') for name in colnamesraw]
        clssz = pd.DataFrame(l, columns=colnames)
        clsszd = clssz.to_dict('records')[1:]
        clsszd = clsszd[:-1]
        d['size'].insert_many(clsszd)
        
        d.logout()
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/') 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        
        doc.add_namespace('doe', 'http://profiles.doe.mass.edu/statereport/')
        
        this_script = doc.agent('alg:emilymo#get_class_sizes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent']})
        get_class_sizes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        class_size_site = doc.entity('doe:classsizebyraceethnicity.aspx', {prov.model.PROV_LABEL:'Massachusetts Class Sizes by District Table', prov.model.PROV_TYPE:'ont:DataResource'})
        size = doc.entity('dat:emilymo#size', {prov.model.PROV_LABEL:'Massachusetts Class Sizes by District', prov.model.PROV_TYPE:'ont:DataSet'})
        
        doc.wasAssociatedWith(get_class_sizes, this_script)
        doc.wasAttributedTo(size, this_script)
        doc.wasGeneratedBy(size, get_class_sizes)
        doc.used(get_class_sizes, class_size_site, other_attributes={prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.wasDerivedFrom(size, class_size_site)
        
        return doc
        
        
        
        


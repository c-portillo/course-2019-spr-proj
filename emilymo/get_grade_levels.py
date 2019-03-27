import dml
from pymongo import MongoClient
import bson.code
import requests 
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import prov.model
import uuid

# Retrieves information about grade levels offered in each Massachusetts school district.

class get_grade_levels(dml.Algorithm):
    contributor = 'emilymo'
    reads = []
    writes = ['d.graderaw']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        client = dml.pymongo.MongoClient() # TO FIX: AUTH??
        d = client.d
        
        site = 'http://profiles.doe.mass.edu/state_report/gradesbydistrict.aspx'
        pg = requests.get(site)
        sp = bs(pg.content, "lxml")
        tbl = sp.find_all('table')[1]
        rows = tbl.find_all('tr')
        l = []
        for tr in rows:
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            l.append(row)
        # this one doesn't have <th> because colnames are included as rows
        precolnames = sp.find_all('tr', {"class": "ccc bold"})
        colnames = [nm.text for nm in precolnames[1].find_all('td')]
        # remove all colnames from rows
        l = [o for o in l if o != colnames]
        grd = pd.DataFrame(l, columns = colnames)
        grdd = grd.to_dict('records')
        # put into Mongo and split up grade levels
        d['graderaw'].insert_many(grdd)
        
        d.logout()
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/') 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        
        doc.add_namespace('doe', 'http://profiles.doe.mass.edu/state_report/')
        
        this_script = doc.agent('alg:emilymo#get_grade_levels', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent']})
        get_grades = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        grade_level_site = doc.entity('doe:gradesbydistrict.aspx', {prov.model.PROV_LABEL:'Massachusetts Grade Levels Offered by School District Table', prov.model.PROV_TYPE:'ont:DataResource'})
        graderaw = doc.entity('dat:emilymo#graderaw', {prov.model.PROV_LABEL:'Massachusetts Grade Levels Offered by School District', prov.model.PROV_TYPE:'ont:DataSet'})
        
        doc.wasAssociatedWith(get_grades, this_script)
        doc.wasAttributedTo(graderaw, this_script)
        doc.wasGeneratedBy(graderaw, get_grades)
        doc.used(get_grades, grade_level_site, other_attributes={prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.wasDerivedFrom(graderaw, grade_level_site)
        
        return doc
        

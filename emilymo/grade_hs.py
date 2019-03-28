import dml
from pymongo import MongoClient
import bson.code
import datetime
import prov.model
import uuid

# Creates data set that tells if a Massachusetts school district offers all grades 9-12 or not.

class grade_hs(dml.Algorithm):
    contributor = 'emilymo'
    reads = ['d.graderaw']
    writes = ['d.grade']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        client = dml.pymongo.MongoClient() # TO FIX: AUTH??
        d = client.d
        
        mapper = bson.code.Code("""
            function() {
                var grdlst = this['Grade List'].split(',');
                if (grdlst.includes('9') &
                    grdlst.includes('10') &
                    grdlst.includes('11') &
                    grdlst.includes('12')) {
                var hs = 1;
                }
                else {
                var hs = 0;
                }
                
                emit(this['_id'], {'districtcode':this['District Code'], 'district':this['District'], 'gradelist':this['Grade List'], 'h':hs})
                
                }
            """)
        reducer = bson.code.Code("""
                function(k, vs) {
                }
                         """)
        d['graderaw'].map_reduce(mapper, reducer, 'grade')
        
        d.logout()
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/') 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        
        this_script = doc.agent('alg:emilymo#grade_hs', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent']})
        grade_hs = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        graderaw = doc.entity('dat:emilymo#graderaw', {prov.model.PROV_LABEL:'Grade Levels by School District', prov.model.PROV_TYPE:'ont:DataResource'})
        grade = doc.entity('dat:emilymo#grade', {prov.model.PROV_LABEL:'Grade Levels by School District with High School Status', prov.model.PROV_TYPE:'ont:DataResource'})
        
        doc.wasAssociatedWith(grade_hs, this_script)
        doc.used(grade_hs, graderaw, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAttributedTo(grade, this_script)
        doc.wasGeneratedBy(grade, grade_hs)
        doc.wasDerivedFrom(grade, graderaw)
        
        return doc
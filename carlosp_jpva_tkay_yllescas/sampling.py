# assuming wards are independent variables

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import math

class sampling(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ['carlosp_jpva_tkay_yllescas.eligible_ward', 'carlosp_jpva_tkay_yllescas.registered_by_ward']
    writes = ['carlosp_jpva_tkay_yllescas.sampling']

    @staticmethod
    def execute(trial = False):
        print("sampling")
        startTime = datetime.datetime.now()
        
        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        
        
        eligible = repo['carlosp_jpva_tkay_yllescas.eligible_ward'].find()
        registered = repo['carlosp_jpva_tkay_yllescas.registered_by_ward'].find()
        
        def sampling(dict, repo):
            for x in repo: 
                for y in x:
                    if y != '_id':
                        for z in x[y]:
                            if z == "Total" or z[0] == "H":
                                if y not in dict:
                                    dict[y] = {}
                                if z not in dict[y]:
                                    dict[y][z] = x[y][z]
                                
            for ward in dict:
                if "H_Total" not in dict[ward]:
                    dict[ward]["H_Total"] = 0
                for category in dict[ward]:
                    if category[0] == "H" and category != "H_Total":
                        dict[ward]["H_Total"] += dict[ward][category]
            
            for ward in dict:
                dict[ward]["H_Prop"] = dict[ward]["H_Total"]/dict[ward]["Total"]

        elig = {}
        sampling(elig, eligible)
        
        regi = {}
        sampling(regi, registered)
                                
        def stat(dict, stats): # dumps statistical analysis about dict into stats 
            prop_total = 0
            prop_count = 0
            for ward in dict:
                prop_total += dict[ward]["H_Prop"]
                prop_count += 1
            prop_mean = prop_total/prop_count    
            stats["prop_mean"] = prop_mean
            for ward in dict: 
                sum = 0
                sum += (dict[ward]["H_Prop"]-prop_mean)**2
            prop_stdev = math.sqrt(sum/prop_count)
            stats["prop_stdev"] = prop_stdev
        
        elig_stats = {}
        regi_stats = {}
        
        stat(elig, elig_stats)
        stat(regi, regi_stats)
        
        stats = {}
        # "E" means eligible, not registered
        # "R" means registered
        # "H" means hispanic
        for ward in elig:
            stats[ward] = {}
            stats[ward]["E_Total"] = elig[ward]["Total"]
            stats[ward]["R_Total"] = regi[ward]["Total"]
            stats[ward]["EH_Total"] = elig[ward]["H_Total"]
            stats[ward]["RH_Total"] = regi[ward]["H_Total"]
            stats[ward]["EH_Prop"] = elig[ward]["H_Prop"]
            stats[ward]["RH_Prop"] = regi[ward]["H_Prop"]
            stats[ward]["Total"] = elig[ward]["Total"] + regi[ward]["Total"]
            stats[ward]["H_Total"] = elig[ward]["H_Total"] + regi[ward]["H_Total"]
            stats[ward]["H_Prop"] = stats[ward]["H_Total"]/stats[ward]["Total"]
        
        stats["aggregate"] = {}
        stats["aggregate"]["R_propMean"] = regi_stats["prop_mean"]
        stats["aggregate"]["E_propMean"] = elig_stats["prop_mean"]
        stats["aggregate"]["R_propstdev"] = regi_stats["prop_stdev"]
        stats["aggregate"]["E_propstdev"] = elig_stats["prop_stdev"]
        stats["aggregate"]["total"] = 0
        stats["aggregate"]["H_total"] = 0
        stats["aggregate"]["R_total"] = 0
        stats["aggregate"]["E_total"] = 0
        stats["aggregate"]["RH_total"] = 0
        stats["aggregate"]["EH_total"] = 0
        
        for ward in elig:
            stats["aggregate"]["total"] += regi[ward]["Total"] + elig[ward]["Total"]
            stats["aggregate"]["H_total"] += regi[ward]["H_Total"] + elig[ward]["H_Total"]            
            stats["aggregate"]["R_total"] += regi[ward]["Total"]            
            stats["aggregate"]["E_total"] += elig[ward]["Total"]            
            stats["aggregate"]["RH_total"] += regi[ward]["H_Total"]            
            stats["aggregate"]["EH_total"] += elig[ward]["H_Total"]            
        
        repo.dropCollection("sampling")
        repo.createCollection("sampling")
        
        wards = []
        for ward in stats:
            if ward[0] == "W" and (stats[ward]["H_Prop"]) > 0.2:
                wards.append(ward)

        repo['carlosp_jpva_tkay_yllescas.sampling'].insert_one(stats)
        repo['carlosp_jpva_tkay_yllescas.sampling'].metadata({'complete':True})
        print(repo['carlosp_jpva_tkay_yllescas.sampling'].metadata())
        
        repo.logout()
        
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#sampling', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        get_sampling = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        eligible_resource = doc.entity('dat:carlosp_jpva_tkay_yllescas#eligible_ward',  {prov.model.PROV_LABEL: 'Eligible Voters', prov.model.PROV_TYPE: 'ont:DataSet'})
        registered_resource = doc.entity('dat:carlosp_jpva_tkay_yllescas#registered_by_ward',  {prov.model.PROV_LABEL: 'Registered Voters', prov.model.PROV_TYPE: 'ont:DataSet'})
        
        sampling = doc.entity('dat:carlosp_jpva_tkay_yllescas#sampling', {prov.model.PROV_LABEL:'Sampling', prov.model.PROV_TYPE:'ont:DataSet'})
            
        doc.wasAssociatedWith(get_sampling, this_script)
        
        doc.usage(get_sampling, eligible_resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'})

        doc.usage(get_sampling, registered_resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'})
        
        doc.wasAttributedTo(sampling, this_script)
        doc.wasDerivedFrom(sampling, eligible_resource, get_sampling, get_sampling, get_sampling)
        doc.wasDerivedFrom(sampling, registered_resource, get_sampling, get_sampling, get_sampling)

        repo.logout()
                  
        return doc
## sampling.execute()

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
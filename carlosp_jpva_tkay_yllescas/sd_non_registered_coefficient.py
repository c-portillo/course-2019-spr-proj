import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import json
import pandas as pd
from pprint import pprint
class sd_non_registered_coefficient(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ['carlosp_jpva_tkay_yllescas.registered', 'carlosp_jpva_tkay_yllescas.non_registered_voters']
    writes = ['carlosp_jpva_tkay_yllescas.sd_non_registered_coefficient']

    @staticmethod

        
    def union(R, S):
        return R + S

    def difference(R, S):
        return [t for t in R if t not in S]

    def intersect(R, S):
        return [t for t in R if t in S]

    def project(R, p):
        return [p(t) for t in R]

    def select(R, s):
        return [t for t in R if s(t)]
     
    def product(R, S):
        return [(t,u) for t in R for u in S]

    def aggregate(R, f):
        keys = {r[0] for r in R}
        return [(key, f([int(v.replace(',', '')) for (k,v) in R if k == key])) for key in keys]


    @staticmethod
    def execute(trial = False):
        print("sd_non_registered_coefficient")
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
       

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        
        #create new collection
        repo.dropCollection("sd_non_registered_coefficient")
        repo.createCollection("sd_non_registered_coefficient")

        s_d_registered = repo['carlosp_jpva_tkay_yllescas.registered']
        s_d_non_registered = repo['carlosp_jpva_tkay_yllescas.non_registered_voters']
        total_caucasian = []
        total_aa = []
        total_hispanic = []
        #basically a select 
        for s_d in s_d_registered.find():
            name = s_d['SD']
            #we know the senate district name now
            #time to aggregate 
            #extract
            total_caucasian.append((name,s_d['C_18_24']))
            total_caucasian.append((name,s_d['C_25_34']))
            total_caucasian.append((name,s_d['C_35_49']))
            total_caucasian.append((name,s_d['C_50_64']))
            total_caucasian.append((name,s_d['C_65+']))
            total_caucasian.append((name,s_d['C_Unknown']))

            total_aa.append((name, s_d['AA_18_24']))
            total_aa.append((name, s_d['AA_25_34']))
            total_aa.append((name, s_d['AA_35_49']))
            total_aa.append((name, s_d['AA_50_64']))
            total_aa.append((name, s_d['AA_65+']))
            total_aa.append((name, s_d['AA_Unknown']))

            total_hispanic.append((name, s_d['H_18_24']))
            total_hispanic.append((name, s_d['H_25_34']))
            total_hispanic.append((name, s_d['H_35_49']))
            total_hispanic.append((name, s_d['H_50_64']))
            total_hispanic.append((name, s_d['H_65+']))
            total_hispanic.append((name, s_d['H_Unknown']))
        #now we can aggregate
        total_caucasian_registered =  sd_non_registered_coefficient.aggregate(total_caucasian,sum)
        total_aa_registered =   sd_non_registered_coefficient.aggregate(total_aa,sum)
        total_hispanic_registered =   sd_non_registered_coefficient.aggregate(total_hispanic,sum)

        total_caucasian = []
        total_aa = []
        total_hispanic = []

        for s_d in s_d_non_registered.find():
            name = s_d['SD']
            #we know the senate district name now
            #time to aggregate 
            #extract
            total_caucasian.append((name,s_d['C_18_24']))
            total_caucasian.append((name,s_d['C_25_34']))
            total_caucasian.append((name,s_d['C_35_49']))
            total_caucasian.append((name,s_d['C_50_64']))
            total_caucasian.append((name,s_d['C_65+']))
            total_caucasian.append((name,s_d['C_Unknown']))

            total_aa.append((name, s_d['AA_18_24']))
            total_aa.append((name, s_d['AA_25_34']))
            total_aa.append((name, s_d['AA_35_49']))
            total_aa.append((name, s_d['AA_50_64']))
            total_aa.append((name, s_d['AA_65+']))
            total_aa.append((name, s_d['AA_Unknown']))

            total_hispanic.append((name, s_d['H_18_24']))
            total_hispanic.append((name, s_d['H_25_34']))
            total_hispanic.append((name, s_d['H_35_49']))
            total_hispanic.append((name, s_d['H_50_64']))
            total_hispanic.append((name, s_d['H_65+']))
            total_hispanic.append((name, s_d['H_Unknown']))

        total_caucasian_non_registered =  sd_non_registered_coefficient.aggregate(total_caucasian,sum)
        total_aa_non_registered =   sd_non_registered_coefficient.aggregate(total_aa,sum)
        total_hispanic_non_registered =   sd_non_registered_coefficient.aggregate(total_hispanic,sum)





        # we have tuples with (senate_district, total) for each ethnicity -> registered/non registered

        #now we can make the % of unregistered voters  -> (senatedistrict,ethnicity, % unregistered)
        percent_of_non_registered_caucasians = {}
        #{'boston': 2000}
        percent_of_non_registered_aa = {}
        #{'boston': 2000}
        percent_of_non_registered_hispanics = {}
        #{'boston': 2000}

        for s_d1 , total_registered in total_caucasian_registered:
            for s_d2 , total_non_registered in total_caucasian_non_registered:
                

                if s_d1 == s_d2:
                    percent = total_non_registered / (total_registered + total_non_registered)
                    percent_of_non_registered_caucasians[s_d1] = percent
                    break;

        for s_d1, total_registered in total_aa_registered:
            for s_d2, total_non_registered in total_aa_non_registered:
                if s_d1 == s_d2:
                    percent = total_non_registered / (total_registered + total_non_registered)
                    percent_of_non_registered_aa[s_d1] = percent
                    break;
        for s_d1, total_registered in total_hispanic_registered:
            for s_d2, total_non_registered in total_hispanic_non_registered:
                if s_d1 == s_d2:
                    percent = total_non_registered / (total_registered + total_non_registered)
                    percent_of_non_registered_hispanics[s_d1] = percent
                    break;

        #now create the new dictionary to upload to mongo
        dictionary_of_coefficients = []
        i = 0
        for s_d1, total_caucasian in total_caucasian_registered:

            name = s_d1
            caucasian =  percent_of_non_registered_caucasians[s_d1]
            aa = percent_of_non_registered_aa[s_d1]
            hispanic =  percent_of_non_registered_hispanics[s_d1]

            dictionary_of_coefficients.append( {name : {'caucasian': caucasian, 'african american': aa , 'hispanic': hispanic } })

        #cool so now we should have ['001 Berkshire, Hampshire, Franklin & Hampden': ]












        
        #census demographics (city,ethnicity, total people, total registered)

        s_d_json = json.dumps(dictionary_of_coefficients)
        s_d_json = json.loads(s_d_json)
        print( s_d_json)

        repo['carlosp_jpva_tkay_yllescas.sd_non_registered_coefficient'].insert_many(s_d_json)
        repo['carlosp_jpva_tkay_yllescas.sd_non_registered_coefficient'].metadata({'complete':True})
        print(repo['carlosp_jpva_tkay_yllescas.sd_non_registered_coefficient'].metadata())


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
        doc.add_namespace('spk', 'https://amplifylatinx.co/')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#sd_non_registered_coefficient', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_sd_non_registered_coefficient = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        registered_input = doc.entity('dat:carlosp_jpva_tkay_yllescas.registered',{prov.model.PROV_LABEL:'Registered',prov.model.PROV_TYPE:'ont:DataSet', 'ont:Query': '.find()'})
        non_registered_input = doc.entity('dat:carlosp_jpva_tkay_yllescas.non_registered_voters',{prov.model.PROV_LABEL:'Non-Registered',prov.model.PROV_TYPE:'ont:DataSet', 'ont:Query': '.find()'})
        output = doc.entity('dat:carlosp_jpva_tkay_yllescas.sd_non_registered_coefficient',
            {prov.model.PROV_LABEL:'Non-Registered voters / Total Voter by Ethnicity byt Senate District', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAssociatedWith(get_sd_non_registered_coefficient, this_script)
        doc.usage(get_sd_non_registered_coefficient, registered_input, startTime, None,
            {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(get_sd_non_registered_coefficient, non_registered_input, startTime, None,
            {prov.model.PROV_TYPE:'ont:Computation'})


        doc.wasAttributedTo(output, this_script)
        doc.wasGeneratedBy(output, get_sd_non_registered_coefficient, endTime)
        doc.wasDerivedFrom(output, registered_input, non_registered_input)


        repo.logout()
                  
        return doc
#sd_non_registered_coefficient.execute()
#d_t = demographics_by_towns
#
#d_t.execute()

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
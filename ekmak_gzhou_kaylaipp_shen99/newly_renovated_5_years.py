import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import zillow
import requests
import xmltodict
import csv
import re

#number of buildings per street in south boston 
class newly_renovated_5_years(dml.Algorithm):
    contributor = 'ekmak_gzhou_kaylaipp_shen99'
    reads = ['ekmak_gzhou_kaylaipp_shen99.permit_data', 'ekmak_gzhou_kaylaipp_shen99.zillow_property_data']
    writes = ['ekmak_gzhou_kaylaipp_shen99.newly_renovated_5_years']

    @staticmethod 
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')

        #list of tuples in format (street name, street num, 1) aka (beacon st  , 362, 1)                  
        #contains all street names and recent date of rennovation for zillow & permit data = union 
        all_year_built = []
        all_construction = []

        #retrieve zillow property data
        zillow_property_data = repo.ekmak_gzhou_kaylaipp_shen99.zillow_property_data.find()
        for info in zillow_property_data:
            full_address = info['address']['street'].lower().replace(".", "")        #25 beacon st
            try:                         
                full_yearBuilt = info['editedFacts']['yearBuilt']   #1880  
            except KeyError as e:             
                continue          
            #get tuples of all addresses and year built in south boston 
            all_year_built.append((full_address, full_yearBuilt))

        #retreieve permit data
        permit_data = repo.ekmak_gzhou_kaylaipp_shen99.permit_data.find()
        for info in permit_data:
            zipcode = info['ZIP']                       #02127
            full_address = info['ADDRESS'].lower().replace(".", "")  #175  w boundary rd
            full_address = re.sub(' +', ' ', full_address)
            pemit_year = info['ISSUED_DATE'][:4]     #2014
            #get all addresses and year of recent construction in south boston
            if zipcode == '02127':
                all_construction.append((full_address, pemit_year))

         
        #combine two data sets
        temp = map (lambda k, v: [(k, ('Year of Built', v))], all_year_built) + reduce (lambda k, v: [(k, ('Year of Recent Construction', v))], all_construction)


        d = {}
        for house in all_year_built: 
            if house[0] not in d: 
                d[house[0]] = [house[1], 0]
        
        for house in all_construction: 
            if house[0] not in d: 
                d[house[0]] = [0, house[1]]
            else: 
                d[house[0]][1] = house[1]

        combined = []
        for st,years in d.items(): 
            combined.append((st,(years[0], years[1])))

        # total = reduce(lambda k,vs:\
        #   (k,(vs[0][1], vs[1][1]) if vs[0][0] == 'Year of Built' else (vs[1][1],vs[0][1])), temp)

        #output should be list of tuples 
        #('address', ('1880', '2015'))

        #get those are constructed within 5 years (after 2014)
        recons_5 = map(lambda k,vs: [(k,vs)] if int(vs[1]) >= 2014 else [], combined) 

        # print('')
        # print('')
        # print(recons_5)

        #create new database 
        repo.dropCollection("newly_renovated_5_years")
        repo.createCollection("newly_renovated_5_years")

        #add to database in {street: count} form 
        for t in combined: 
            repo['ekmak_gzhou_kaylaipp_shen99.newly_renovated_5_years'].insert_one({t[0]:t[1]})

        print('inserted newly renovated within 5 years data')
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
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_agent = doc.agent('alg:ekmak_gzhou_kaylaipp_shen99#newly_renovated_5_years',
		                      	{prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        this_entity = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#newly_renovated_5_years',
                            {prov.model.PROV_LABEL: 'Number of Newly Renovated Houses', prov.model.PROV_TYPE: 'ont:DataSet'})

        permit_data_resource = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#permit_data',
		                  {prov.model.PROV_LABEL: 'Permit Data', prov.model.PROV_TYPE: 'ont:DataSet'})

        zillow_property_data_resource = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#zillow_property_data',
		                  {prov.model.PROV_LABEL: 'Zillow Property Data', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_num_houses_5_years = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.usage(get_num_houses_5_years, permit_data_resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(get_num_houses_5_years, zillow_property_data_resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        doc.wasAssociatedWith(get_num_houses_5_years, this_agent)

        doc.wasAttributedTo(this_entity, this_agent)

        doc.wasGeneratedBy(this_entity, get_num_houses_5_years, endTime)

        doc.wasDerivedFrom(this_entity, permit_data_resource, zillow_property_data_resource, get_num_houses_5_years, get_num_houses_5_years, get_num_houses_5_years)

        repo.logout()
                  
        return doc

# def map(f, R):
#     return [t for (k,v,s) in R for t in f(k,v)]

def map(f, R):
    return [t for (k,v) in R for t in f(k,v)]
    
def reduce(f, R):
    keys = {k for (k,v) in R}
    return [f(k1, [v for (k2,v) in R if k1 == k2]) for k1 in keys]

def project(R, p):
    return [p(t) for t in R]


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

# newly_renovated_5_years.execute()
# print('generating newly renovated house provenance...')
# doc = newly_renovated_5_years.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

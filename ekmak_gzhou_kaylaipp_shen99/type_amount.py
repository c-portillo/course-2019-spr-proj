import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
#import zillow
import requests
import xmltodict
import csv

#number of buildings per street in south boston 
class type_amount(dml.Algorithm):
    contributor = 'ekmak_gzhou_kaylaipp_shen99'
    reads = ['ekmak_gzhou_kaylaipp_shen99.zillow_property_data', 'ekmak_gzhou_kaylaipp_shen99.zillow_getsearchresults_data']
    writes = ['ekmak_gzhou_kaylaipp_shen99.type_amount']

    @staticmethod 
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')

        #list of tuples in format (street name, street num, 1) aka (beacon st  , 362, 1)                  
        #contains all street names for accessing & address data = union 
        unit_bed_bath = []
        unit_amount = []

        property_data = repo.ekmak_gzhou_kaylaipp_shen99.zillow_property_data.find()
        for info in property_data:
            st_full = info['address']['street'] 
            types = info['editedFacts']['useCode']

            unit_bed_bath.append((st_full, types))

        search_results_data = repo.ekmak_gzhou_kaylaipp_shen99.zillow_getsearchresults_data.find()
        for info in search_results_data: 
            st_full = info['full_address']['street']     
            amount = info['zestimate']['amount']
  
            unit_amount.append((st_full, amount))

        selected = select(unit_amount, lambda t: t[1] != None)

        all_units = [(t,u) for t in selected for u in unit_bed_bath]
    
        combine = select(all_units, lambda t: t[0][0] == t[1][0])

        concatonate = project(combine, lambda t: (t[1][1], (t[0][1], 1)))

        #print(concatonate[2])

        avgagg = reduce(lambda k,v: (k,sum(v[0])/sum(v[1])), concatonate)

        #print(avgagg[0])

        #create new database 
        repo.dropCollection("type_amount")
        repo.createCollection("type_amount")

        #add to database in {street: count} form 
        for t in avgagg: 
            repo['ekmak_gzhou_kaylaipp_shen99.type_amount'].insert_one({t[0]:t[1]})

        print('inserted number of bedrooms, bathrooms, and amount')
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

        this_agent = doc.agent('alg:ekmak_gzhou_kaylaipp_shen99#type_amount',
		                      	{prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        this_entity = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#type_amount',
                            {prov.model.PROV_LABEL: 'Type and Amount', prov.model.PROV_TYPE: 'ont:DataSet'})

        property_data_resource = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#zillow_property_data',
		                  {prov.model.PROV_LABEL: 'Property Data', prov.model.PROV_TYPE: 'ont:DataSet'})

        getsearchresult_resource = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#zillow_getsearchresults_data',
		                  {prov.model.PROV_LABEL: 'getSearchResults', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_type_amount = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.usage(get_type_amount, property_data_resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(get_type_amount, getsearchresult_resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        doc.wasAssociatedWith(get_type_amount, this_agent)

        doc.wasAttributedTo(this_entity, this_agent)

        doc.wasGeneratedBy(this_entity, get_type_amount, endTime)

        doc.wasDerivedFrom(this_entity, property_data_resource, getsearchresult_resource, get_type_amount, get_type_amount, get_type_amount)

        repo.logout()
                  
        return doc

def map(f, R):
    return [t for (k,v,s) in R for t in f(k,v)]
    
def reduce(f, R):
    keys = {k for (k,v) in R}
    return [f(k1, [v for (k2,v) in R if k1 == k2]) for k1 in keys]
def project(R, p):
    return [p(t) for t in R]
def product(R, S):
    return [(t,u) for t in R for u in S]
def select(R, s):
    return [t for t in R if s(t)]


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

# type_amount.execute()
# print('generating num houses per street provenance...')
# print('')
# doc = type_amount.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

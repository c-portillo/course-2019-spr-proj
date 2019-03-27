import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import pandas as pd

class example(dml.Algorithm):
    contributor = 'arshadr_rcallah_shaikh1'
    reads = []
    #writes = ['arshadr_rcallah_shaikh1.assessor18', 'arshadr_rcallah_shaikh1.permits', 'arshadr_rcallah_shaikh1.incomes']
    writes = ['arshadr_rcallah_shaikh1.rental_prices', 'arshadr_rcallah_shaikh1.home_values', 'arshadr_rcallah_shaikh1.property_values']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('arshadr_rcallah_shaikh1', 'arshadr_rcallah_shaikh1')

        # Zillow rent prices
        # url = 'http://datamechanics.io/data/arshadr_rcallah_shaikh1/City_ZriPerSqft_AllHomes.json'
        url = 'http://files.zillowstatic.com/research/public/City/City_ZriPerSqft_AllHomes.csv'
        urllib.request.urlretrieve(url, 'rent-prices.csv')
        r = pd.read_csv('rent-prices.csv', encoding="ISO-8859-1").to_json()

        r = json.loads(r)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("rental_prices")
        repo.createCollection("rental_prices")
        repo['arshadr_rcallah_shaikh1.rental_prices'].insert_one(r)
        repo['arshadr_rcallah_shaikh1.rental_prices'].metadata({'complete':True})
        print(repo['arshadr_rcallah_shaikh1.rental_prices'].metadata())

        # Zillow single family home buying prices
        # url = 'http://datamechanics.io/data/arshadr_rcallah_shaikh1/City_Zhvi_SingleFamilyResidence.json'
        url = 'http://files.zillowstatic.com/research/public/Metro/Metro_Zhvi_Summary_AllHomes.csv'
        urllib.request.urlretrieve(url, 'single-family-prices.csv')
        r = pd.read_csv('single-family-prices.csv', encoding="ISO-8859-1").to_json()

        r = json.loads(r)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("home_values")
        repo.createCollection("home_values")
        repo['arshadr_rcallah_shaikh1.home_values'].insert_one(r)


        # Fiscal year 2019 Chelsea property data (https://www.chelseama.gov/assessor/pages/chelsea-property-data)
        url = "https://www.chelseama.gov/home/files/housing-data"
        urllib.request.urlretrieve(url, "housing-data.xls")
        r = pd.read_excel('./housing-data.xls').to_json()

        r = json.loads(r)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("property_values")
        repo.createCollection("property_values")
        repo['arshadr_rcallah_shaikh1.property_values'].insert_one(r)

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
        repo.authenticate('arshadr_rcallah_shaikh1', 'arshadr_rcallah_shaikh1')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('zlo', 'https://www.zillow.com/')
        doc.add_namespace('chl', 'https://www.chelseama.gov/assessor/pages/')

        this_script = doc.agent('alg:arshadr_rcallah_shaikh1#example', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('zlo:research/data/', { prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource = doc.entity('zlo:research/data/', { prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource = doc.entity('chl:chelsea-property-data', { prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_rent = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_buying = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_property = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_rent, this_script)
        doc.wasAssociatedWith(get_buying, this_script)
        doc.wasAssociatedWith(get_property, this_script)
        doc.usage(get_rent, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                   'ont:Retrieval':''
                   }
                  )
        doc.usage(get_buying, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                   'ont:Retrieval':''
                   }
                  )
        doc.usage(get_property, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                   'ont:Retrieval':''
                   }
                  )

        rent = doc.entity('zlo:research/data/', {prov.model.PROV_LABEL:'Rent Prices', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(rent, this_script)
        doc.wasGeneratedBy(rent, get_rent, endTime)
        doc.wasDerivedFrom(rent, resource, get_rent, get_rent, get_rent)

        buying = doc.entity('zlo:research/data/', {prov.model.PROV_LABEL:'Buying Prices', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(buying, this_script)
        doc.wasGeneratedBy(buying, get_buying, endTime)
        doc.wasDerivedFrom(buying, resource, get_buying, get_buying, get_buying)

        property = doc.entity('chl:chelsea-property-data', {prov.model.PROV_LABEL:'Property Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(property, this_script)
        doc.wasGeneratedBy(property, get_property, endTime)
        doc.wasDerivedFrom(property, resource, get_property, get_property, get_property)


        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# example.execute()
'''
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
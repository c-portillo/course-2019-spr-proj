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


class get_zillow_search_data(dml.Algorithm):

    contributor = 'ekmak_gzhou_kaylaipp_shen99'
    reads = []
    writes = ['ekmak_gzhou_kaylaipp_shen99.zillow_getsearchresults_data']

    @staticmethod
    def execute(trial = True):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        #connect to database
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')

        # #Retrieve Zillow Search Data - souce: Zillow API and uploaded to datamechanics.io
        url = 'http://datamechanics.io/data/zillow_getsearchresults_data.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s =json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("zillow_getsearchresults_data")
        repo.createCollection("zillow_getsearchresults_data")
        for info in r:
            repo['ekmak_gzhou_kaylaipp_shen99.zillow_getsearchresults_data'].insert_one(info)
        repo['ekmak_gzhou_kaylaipp_shen99.zillow_getsearchresults_data'].metadata({'complete':True})
        print(repo['ekmak_gzhou_kaylaipp_shen99.zillow_getsearchresults_data'].metadata())
        print('inserted zillow search data')
        
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

        this_script = doc.agent('alg:ekmak_gzhou_kaylaipp_shen99#get_zillow_search_data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:zillow_getsearchresults_data', {'prov:label':'Zillow Search Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})

        get_zillow_search_data = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_zillow_search_data, this_script)
        doc.usage(get_zillow_search_data, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        zillow_search_data = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#get_zillow_search_data', {prov.model.PROV_LABEL:'Zillow Search Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(zillow_search_data, this_script)
        doc.wasGeneratedBy(zillow_search_data, get_zillow_search_data, endTime)
        doc.wasDerivedFrom(zillow_search_data, resource, get_zillow_search_data, get_zillow_search_data, get_zillow_search_data)

        repo.logout()
                  
        return doc


'''

Helper functions to retrieve data 

'''
#connect to zillow api
zillow_key = 'X1-ZWz1gx7ezhy3uz_9abc1'
api = zillow.ValuationApi()

#params: address,city,zipcode
#returns: dictionary of property data 
def get_property_results(address, city, state, zipcode): 
    #create empty dictionary to store results 
    # house_details = {}
    full_address = address + ',' + city + ',' + state
    #first get zillow pid
    data = api.GetSearchResults(zillow_key, full_address, zipcode)
    zpid = data.zpid

    zillow_property_details = 'http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm?zws-id=' + zillow_key + '&zpid=' + zpid
    prop_details = requests.get(zillow_property_details)

    data = prop_details.content.decode('utf-8')
    xmltodict_data = xmltodict.parse(data)
    
    json_data = json.dumps(xmltodict_data)
    json_data = json.loads(json_data)

    api_code = json_data['UpdatedPropertyDetails:updatedPropertyDetails']['message']['code']

    if api_code == '0': 
        response = json_data['UpdatedPropertyDetails:updatedPropertyDetails']['response']
        return response


def retrieve_zillow_property_data(): 
    result = []
    CSV_URL = 'http://datamechanics.io/data/Live_Street_Address_Management_SAM_Addresses.csv'
    with requests.get(CSV_URL, stream=True) as r:
        print('retrieving zillow property data from API')
        lines = (line.decode('utf-8') for line in r.iter_lines())
        idx = 0
        for row in csv.reader(lines):
            zipcode = row[20]
            street = row[5]
            if zipcode == '02127': 
                idx += 1
                try:
                    data = get_property_results(street, 'Boston', 'MA', zipcode)
                except zillow.error.ZillowError as e: 
                    print('error')
                    continue
                result.append(data)
    #write out results to file
    with open('zillow_property_data.json', 'w') as outfile:
        print('outputing file')
        json.dump(result, outfile)



key = 'X1-ZWz182me3104qz_6wmn8'
api = zillow.ValuationApi()

def retrieve_zillow_searchresults_data():
    result = []
    CSV_URL = 'http://datamechanics.io/data/Live_Street_Address_Management_SAM_Addresses.csv'
    with requests.get(CSV_URL, stream=True) as r:
        lines = (line.decode('utf-8') for line in r.iter_lines())
        index = 0
        for row in csv.reader(lines):
            zipcode = row[20]
            street = row[5]
            if zipcode == '02127':
                index += 1
                address = street + ", Boston, MA"
                try: 
                    data = api.GetSearchResults(key, address, zipcode).get_dict()
                except zillow.error.ZillowError as e: 
                    print('error')
                    continue
                result.append(data)
    with open('zillow_getsearchresults_data.json', 'w') as outfile:
        print('outputting file')
        json.dump(result, outfile)





'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
# get_zillow_search_data.execute()
## eof

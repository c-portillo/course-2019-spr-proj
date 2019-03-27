
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv 
import io
import time
#get the data about neighborhoods

class supermarket(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = []
    writes = ['henryhcy_wangyp.supermarket']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        allston = '42.3529,-71.1321'
        backbay = '42.3507752636,-71.0748797005'
        beacon_hill ='42.3587999,-71.0707389'
        brighton ='42.317980,-71.158510'
        charlestown ='42.392600,-71.093980'
        chinatown = '42.347960,-71.056410'
        Dochester = '42.299780,-71.078840'
        downtown = '42.355300,-71.055280'
        east_boston ='42.375401,-71.039482'
        fenway_kenmore = '42.345480,-71.101700'
        Hyde_Park = '42.255810,-71.124130'
        Jamaica_Plain = '42.310880,-71.125060'
        Mattapan = '42.252160,-71.124950'
        Mission_Hill = '42.334000,-71.097910'
        North_end = '42.365530,-71.060880'
        Roslindale = '42.317980,-71.158510'
        Roxbury ='42.317980,-71.158510'
        south_end = '42.332670,-71.097910'
        south_boston ='42.337541,-71.042942'
        west_end = '42.364397,-71.065958'
        west_roxbury = '42.284392,-71.161520'
        bos_loc = "42.3600825,-71.0588801"

        locations = [allston,backbay,beacon_hill,brighton,charlestown,chinatown,Dochester,downtown,east_boston,fenway_kenmore,
                    Hyde_Park,Jamaica_Plain,Mattapan,Mission_Hill,North_end,Roslindale,Roxbury,south_end,south_boston,west_end
                    ,west_roxbury,bos_loc]

        key = dml.auth['services']['googleprotocal']['key']

        prefix = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        _type = 'grocery_or_supermarket'
        radius = '50000'
        next_pg_token = []
        data = []

        for location in locations:
            
            url = prefix +'location='+location+"&radius="+radius+"&type="+_type+"&key="+key
         
            response = urllib.request.urlopen(url).read().decode("utf-8")
            r = json.loads(response)
            count = 0
            
            while ('next_page_token' in r):
                count += 1
                
                nextpg=r['next_page_token']

                data = data + (r['results'])

                url = prefix+"pagetoken="+nextpg+"&key="+key

                response = urllib.request.urlopen(url).read().decode()
                r = json.loads(response)
                while (r['status'] == 'INVALID_REQUEST'):
                    time.sleep(.300)
                    response = urllib.request.urlopen(url).read().decode()
                    r = json.loads(response)
            data = data + r['results']
        
        #clean up the data
        supermarket = []
        ids = []
        for x in data:
            temp = {}
            if x['id'] not in ids:
                ids.append(x['id'])
                temp['name'] = x['name']
                temp['types'] = x['types']
                if 'price_level' in x:
                    temp['price_level'] = x['price_level']
                else:
                    temp['price_level'] = 'N/A'
               
                temp['address'] = x['vicinity']
                temp['neighborhood'] = x['vicinity'].split(',')[1].strip()
                supermarket.append(temp)
            else:
                continue
        

        repo.dropCollection("supermarket")
        repo.createCollection("supermarket")
        repo['henryhcy_wangyp.supermarket'].insert_many(supermarket)
        repo['henryhcy_wangyp.supermarket'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.supermarket'].metadata())
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
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/henryhcy_wangyp/')

        this_script = doc.agent('alg:henryhcy_wangyp#supermarket', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:household_supermarket.json', {'prov:label':'supermarket information', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_supermarket = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_supermarket, this_script)
        doc.usage(get_supermarket, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=supermarket&$select=name,types,price_level,neighborhood,address,OPEN_DT'
                  }
                  )
        


        supermarket = doc.entity('dat:henryhcy_wangyp#supermarket', {prov.model.PROV_LABEL:'supermarket', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(supermarket, this_script)
        doc.wasGeneratedBy(supermarket, get_supermarket, endTime)
        doc.wasDerivedFrom(supermarket, resource, get_supermarket, get_supermarket, get_supermarket)

        

        repo.logout()
                  
        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
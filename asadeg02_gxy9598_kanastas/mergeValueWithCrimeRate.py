import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from bson.code import Code
import time
import selenium
from selenium import webdriver


class mergeValueWithCrimeRate(dml.Algorithm):
    
    contributor = 'asadeg02_gxy9598'
    reads = ['asadeg02_gxy9598.address_crime_rate']
    writes = ['asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods']

    @staticmethod
    def scrapeBostonGov(address_list):

        start_time = time.time()
        print("Scraping Boston gov for details of properties")
        #driver = webdriver.Chrome("/usr/bin/chromedriver")
        #driver.get("https://www.cityofboston.gov/assessing/search/")

        results = []    

        for address in address_list:

            driver = webdriver.Chrome("/usr/bin/chromedriver")
            driver.get("https://www.cityofboston.gov/assessing/search/")

            search_field = driver.find_element_by_xpath("//input[@type='search']")
            search_field.send_keys(address)

            submit = driver.find_element_by_xpath("//input[@type='submit']")
            submit.click()

            if len(driver.find_elements_by_tag_name("table")) >= 4:
                table = driver.find_elements_by_tag_name("table")[3]
                rows = table.find_elements_by_tag_name("tr")

                for row in rows:

                    columns = (row.find_elements_by_tag_name("td"))
                    data = {}
                    data_keys = ["PARCEL ID", "ADDRESS", "OWNER", "VALUE"]
                    for i in range (0, len(columns) -2):
                        data[data_keys[i]] = columns[i].text        
                        if len(data.keys()) > 0:
                            results.append(data)
            driver.close()

        elapsed_time = time.time() - start_time
        print("Time elapsed: " + str(elapsed_time))
        print("Finished scraping Boston gov for details of properties")
        return results
  
    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asadeg02_gxy9598', 'asadeg02_gxy9598')        

        address_crime_rate =  repo.asadeg02_gxy9598.address_crime_rate.find()

        print(address_crime_rate)
        #sort crime rates in assending order
        rates = []
        for doc in address_crime_rate:            
            rates.append(int(doc['value']))            
        rates = list(set(rates))
        rates.sort(reverse=True)
          

        
        rates = rates[:1]        
        #merge by initial address_crime_rate dataset        
        address_crime_rate =  repo.asadeg02_gxy9598.address_crime_rate.find()
        sorted_crime_rates = []
        for doc in address_crime_rate:            
            if int(doc['value']) in rates:
                sorted_crime_rates.append(doc)        
        
        address_list = []
        for doc in sorted_crime_rates:
            if doc['_id'] != '':
                address_list.append(doc['_id']) 
       
        
        results = mergeValueWithCrimeRate.scrapeBostonGov(address_list)
        

        repo.dropCollection('asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods')
        repo.createCollection('asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods')     
        #repo['asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods'].insert_many(results) 
        _id = 0
        for r in results:
            r['_id'] = _id
            repo["asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods"].insert(r)
            _id += 1
        repo['asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods'].metadata({'complete':True})
        print(repo['asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods'].metadata())
        print('Load Propert Value For the most dangerous Neighbourhoods')
        repo.logout()
        endTime = datetime.datetime.now()
        return {"Start ":startTime, "End ":endTime}

      ###############################################################################################################################################

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asadeg02_gxy9598', 'asadeg02_gxy9598')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('cob', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bod', 'http://bostonopendata.boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:asadeg02_gxy9598#mergeValueWithCrimeRate', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})        
        merge_value_with_crime_rate = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime, 
                                        {'prov:label':'Finds The Property Value Of Properties In Dangerouse', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(merge_value_with_crime_rate, this_script) 
        
        resource_crimes_incident = doc.entity('dat:asadeg02_gxy9598#address_crime_rate', {prov.model.PROV_LABEL:'Address Crime Rate', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_property_value = doc.entity('cob:', {'prov:label':'Real Estate Assessments', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        doc.usage(merge_value_with_crime_rate, resource_crimes_incident, startTime)
        doc.usage(merge_value_with_crime_rate, resource_property_value, startTime)

        property_value_for_dangerous_neighbourhoods = doc.entity('dat:asadeg02_gxy9598#property_value_for_dangerous_neighbourhoods', 
                                       {prov.model.PROV_LABEL:'Value for Properties In Dangereous Neighbourhoods ', prov.model.PROV_TYPE:'ont:DataSet'})

        doc.wasAttributedTo(property_value_for_dangerous_neighbourhoods, this_script)
        doc.wasGeneratedBy(property_value_for_dangerous_neighbourhoods, merge_value_with_crime_rate, endTime)
        doc.wasDerivedFrom(property_value_for_dangerous_neighbourhoods, resource_crimes_incident, merge_value_with_crime_rate, merge_value_with_crime_rate, merge_value_with_crime_rate)
        doc.wasDerivedFrom(property_value_for_dangerous_neighbourhoods, resource_property_value, merge_value_with_crime_rate, merge_value_with_crime_rate, merge_value_with_crime_rate)
        
        repo.logout()
        return doc






mergeValueWithCrimeRate.execute()
doc = mergeValueWithCrimeRate.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))
## eof

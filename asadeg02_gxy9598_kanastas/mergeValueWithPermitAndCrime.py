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


class mergeValueWithPermitAndCrime(dml.Algorithm):
    
    contributor = 'asadeg02_gxy9598'
    reads = ['asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods', 
            'asadeg02_gxy9598.building_permits', 'asadeg02_gxy9598.crime_incident_report']
    writes = ['address_value_crime_rate_permit_number']     
  
    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asadeg02_gxy9598', 'asadeg02_gxy9598')        

        property_value_for_dangerous_neighbourhoods =  repo.asadeg02_gxy9598.property_value_for_dangerous_neighbourhoods.find()
        building_permits = repo.asadeg02_gxy9598.building_permits.find()
        crime_incidents = repo.asadeg02_gxy9598.crime_incident_report.find()

        
        #create a dictionary for buiding permits with parcel id as key
        buidling_permits_dict = {}        
        for doc in building_permits:
            key = doc['Parcel_ID'] 
            buidling_permits_dict[key]  = doc               
        
        #merge with building permit data base
        address_crime_rate_permit_number_data = []
        for doc in property_value_for_dangerous_neighbourhoods:            
            if doc['PARCEL ID'] in buidling_permits_dict:
                building_permit_doc = buidling_permits_dict[doc['PARCEL ID']]
                doc['PermitNumber'] = building_permit_doc['PermitNumber']
                doc['city'] = building_permit_doc['CITY']
                doc['applicant'] = building_permit_doc['APPLICANT']
                doc['status'] = building_permit_doc['STATUS']
                doc['comments'] = building_permit_doc['Comments']
                doc['work_type'] = building_permit_doc['WORKTYPE']
                address_crime_rate_permit_number_data.append(doc)      
        

        #create a dictionary for crime incidents with street name as address
        crime_incidents_dict = {}        
        for doc in crime_incidents:
            key = doc['street']
            if key in crime_incidents_dict: 
                crime_incidents_dict[key].append(doc)
            else:
                crime_incidents_dict[key] = [doc]

        #merge with crime incident
        merged_data = []       
        for data in address_crime_rate_permit_number_data:            
            street = data['ADDRESS'].split(" ", 1)[1]            
            if street in crime_incidents_dict:
                for doc in crime_incidents_dict[street]:                                    
                    data['offense_description']  = doc['offense_description']
                    data['offense_code_group']  = doc['offense_code_group']            
                    merged_data.append(data)        

       
        repo.dropCollection('asadeg02_gxy9598.address_value_crime_rate_permit_number')
        repo.createCollection('asadeg02_gxy9598.address_value_crime_rate_permit_number')

        _id = 0
        for doc in merged_data:
            doc['_id'] = _id
            _id += 1              
            repo["asadeg02_gxy9598.address_value_crime_rate_permit_number"].insert(doc)

        repo["asadeg02_gxy9598.address_value_crime_rate_permit_number"].metadata({'complete':True})
        print(repo["asadeg02_gxy9598.address_value_crime_rate_permit_number"].metadata())
        print('Finished Merging')

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

        this_script = doc.agent('alg:asadeg02_gxy9598#mergeValueWithPermitAndCrime', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})        
        mergeValueWithPermitAndCrime = doc.activity('log:uuid'+ str(uuid.uuid4()), startTime, endTime, 
                                        {'prov:label':'Finds permit number of buidings and types of in the dangerous neighbourhood  ', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(mergeValueWithPermitAndCrime, this_script) 
        
        resource_crimes_incident = doc.entity('dat:asadeg02_gxy9598#address_crime_rate', {prov.model.PROV_LABEL:'Address Crime Rate', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_buiding_permits = doc.entity('dat:asadeg02_gxy9598#building_permits', {prov.model.PROV_LABEL:'Buiding Permits', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_property_value_for_dangerous_neighbourhoods = doc.entity('dat:asadeg02_gxy9598#property_value_for_dangerous_neighbourhoods', {prov.model.PROV_LABEL:'Property Value For Dangerous Neighbourhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(mergeValueWithPermitAndCrime, resource_crimes_incident, startTime)
        doc.usage(mergeValueWithPermitAndCrime, resource_buiding_permits, startTime)
        doc.usage(mergeValueWithPermitAndCrime, resource_property_value_for_dangerous_neighbourhoods, startTime)

        address_value_crime_rate_permit_number = doc.entity('dat:asadeg02_gxy9598#address_value_crime_rate_permit_number', 
                                       {prov.model.PROV_LABEL:'Address And Value And Crimerate And Permit Number of Buildings In Dangerous Neighbourhoods', prov.model.PROV_TYPE:'ont:DataSet'})

        doc.wasAttributedTo(address_value_crime_rate_permit_number, this_script)
        doc.wasGeneratedBy(address_value_crime_rate_permit_number, mergeValueWithPermitAndCrime, endTime)
        doc.wasDerivedFrom(address_value_crime_rate_permit_number, resource_crimes_incident, mergeValueWithPermitAndCrime, mergeValueWithPermitAndCrime, mergeValueWithPermitAndCrime)
        doc.wasDerivedFrom(address_value_crime_rate_permit_number, resource_buiding_permits, mergeValueWithPermitAndCrime, mergeValueWithPermitAndCrime, mergeValueWithPermitAndCrime)
        doc.wasDerivedFrom(address_value_crime_rate_permit_number, resource_property_value_for_dangerous_neighbourhoods, mergeValueWithPermitAndCrime, mergeValueWithPermitAndCrime, mergeValueWithPermitAndCrime)
        
        repo.logout()
        return doc






mergeValueWithPermitAndCrime.execute()
doc = mergeValueWithPermitAndCrime.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))
## eof

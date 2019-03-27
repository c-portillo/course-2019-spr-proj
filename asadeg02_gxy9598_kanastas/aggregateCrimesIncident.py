import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from bson.code import Code


class aggregateCrimesIncident(dml.Algorithm):

    contributor = 'asadeg02_gxy9598'
    reads = ['asadeg02_gxy9598.crime_incident_report']
    writes = ['asadeg02_gxy9598.address_crime_rate']

    
    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asadeg02_gxy9598', 'asadeg02_gxy9598')

        repo.dropPermanent('asadeg02_gxy9598.address_crime_rate')
        repo.createPermanent('asadeg02_gxy9598.address_crime_rate')

        
        
        crimes =  repo.asadeg02_gxy9598.crime_incident_report.find()
        
        #count aggregation using address as keys
        mapper = Code("function () {"                   
                   "   emit(this.street, 1);"
                   "}")

        reducer = Code("function (key, values) {"
                          "return Array.sum(values);"
                      "}")
        
        repo.asadeg02_gxy9598.crime_incident_report.map_reduce(mapper, reducer, 'asadeg02_gxy9598.address_crime_rate')
        
        repo["asadeg02_gxy9598.address_crime_rate"].metadata({'complete':True})
        print(repo["asadeg02_gxy9598.address_crime_rate"].metadata())
        print('Load Address crime rate')       
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

        this_script = doc.agent('alg:asadeg02_gxy9598#aggregateCrimesIncident', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})        
        aggregate_crimes_incident= doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime, {'prov:label':'Counts The Number Of Crime per Address', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(aggregate_crimes_incident, this_script)
 
        resource_crimes_incident = doc.entity('dat:asadeg02_gxy9598#crime_incident_report', {prov.model.PROV_LABEL:'Crime Incident Report', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(aggregate_crimes_incident, resource_crimes_incident, startTime)

        address_crime_rate = doc.entity('dat:asadeg02_gxy9598#address_crime_rate', {'prov:label':'Number Of Incidents Per Address', prov.model.PROV_TYPE:'ont:Dataset'})
        doc.wasAttributedTo(address_crime_rate, this_script)
        doc.wasGeneratedBy(address_crime_rate, aggregate_crimes_incident, endTime)
        doc.wasDerivedFrom(address_crime_rate, resource_crimes_incident, aggregate_crimes_incident, aggregate_crimes_incident, aggregate_crimes_incident)
        
        repo.logout()
        return doc






aggregateCrimesIncident.execute()
doc = aggregateCrimesIncident.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))
## eof

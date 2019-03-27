import geopandas
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class race_and_ethnicity(dml.Algorithm):
    contributor = 'hek_kquirk'
    reads = []
    writes = ['hek_kquirk.race_and_ethnicity', 'hek_kquirk.neighborhood_district']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hek_kquirk', 'hek_kquirk')

        url = 'http://datamechanics.io/data/hek_kquirk/race_and_ethnicity.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("race_and_ethnicity")
        repo.createCollection("race_and_ethnicity")
        repo['hek_kquirk.race_and_ethnicity'].insert_many(r)
        repo['hek_kquirk.race_and_ethnicity'].metadata({'complete':True})
        print(repo['hek_kquirk.race_and_ethnicity'].metadata())
        
        url = 'http://datamechanics.io/data/hek_kquirk/neighborhood_district.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("neighborhood_district")
        repo.createCollection("neighborhood_district")
        repo['hek_kquirk.neighborhood_district'].insert_many(r)
        repo['hek_kquirk.neighborhood_district'].metadata({'complete':True})
        print(repo['hek_kquirk.neighborhood_district'].metadata())

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
        repo.authenticate('hek_kquirk', 'hek_kquirk')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:hek_kquirk#race_and_ethnicity', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        resource_race = doc.entity('dat:hek_kquirk/race_and_ethnicity.json', {'prov:label':'Data Mechanics Race and Ethincity', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource_neighborhood = doc.entity('dat:hek_kquirk/neighborhood_district.json', {'prov:label':'Data Mechanics Boston Neighborhood to Police Districts', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_race_and_ethnicity = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_neighborhood_district = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_race_and_ethnicity, this_script)
        doc.wasAssociatedWith(get_neighborhood_district, this_script)
        doc.usage(get_race_and_ethnicity, resource_race, startTime, None,
                  {
                      prov.model.PROV_TYPE:'ont:Retrieval'
                  }
        )
        doc.usage(get_neighborhood_district, resource_neighborhood, startTime, None,
                  {
                      prov.model.PROV_TYPE:'ont:Retrieval'
                  }
        )

        race_and_ethnicity = doc.entity('dat:hek_kquirk#race_and_ethnicity', {prov.model.PROV_LABEL:'Boston Neighborhoods Race and Ethnicity Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(race_and_ethnicity, this_script)
        doc.wasGeneratedBy(race_and_ethnicity, get_race_and_ethnicity, endTime)
        doc.wasDerivedFrom(race_and_ethnicity, resource_race, get_race_and_ethnicity, get_race_and_ethnicity, get_race_and_ethnicity)

        neighborhood_district = doc.entity('dat:hek_kquirk#neighborhood_district', {prov.model.PROV_LABEL:'Boston Neighborhood to Police Districts', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(neighborhood_district, this_script)
        doc.wasGeneratedBy(neighborhood_district, get_neighborhood_district, endTime)
        doc.wasDerivedFrom(neighborhood_district, resource_neighborhood, get_neighborhood_district, get_neighborhood_district, get_neighborhood_district)

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

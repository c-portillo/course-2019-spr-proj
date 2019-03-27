import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class fire_building_transformation(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = ['liweixi_mogujzhu.fire_incident_report','liweixi_mogujzhu.building_and_property_violations']
    writes = ['liweixi_mogujzhu.fire_building_transformation']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')
        repo.dropCollection("fire_building_transformation")
        repo.createCollection("fire_building_transformation")

        # get all fire incident objects
        fire_incident = list(repo["liweixi_mogujzhu.fire_incident_report"].find())
    
        # get all violate buildings objects 
        building_violations = list(repo["liweixi_mogujzhu.building_and_property_violations"].find())

        # compute the number of violate buildings on every street
        building_street_dict = {}
        for building in building_violations:
            if building['Street'] is None:
                continue
            if building['Street'].strip() not in building_street_dict:
                building_street_dict[building['Street'].strip()] = 1
            else:
                building_street_dict[building['Street'].strip()] += 1
        
        # compute the number of fire incidents on every street
        fire_street_dict = {}
        for fire in fire_incident:
            if fire['Street Name'] is None:
                continue
            if fire['Street Name'].strip() not in fire_street_dict:
                fire_street_dict[fire['Street Name'].strip()] = 1
            else:
                fire_street_dict[fire['Street Name'].strip()] += 1
            
        # print(sorted(fire_street_dict.items(),key=lambda item:item[1] ))
        
        # create a new dataset contains the street name, # of fire incidents and # of violate buildings
        new_combined_dataset = []
        for key in building_street_dict:
            if key.upper() in fire_street_dict:
                new_combined_dataset.append({'Street Name':key.upper(), 'Fire Incident Number':fire_street_dict[key.upper()], 'Building Violation Number':building_street_dict[key]})
            else:
                new_combined_dataset.append({'Street Name':key.upper(), 'Fire Incident Number':0, 'Building Violation Number':building_street_dict[key]})
        
        for key in fire_street_dict:
            if key.title() not in building_street_dict:
                new_combined_dataset.append({'Street Name':key, 'Fire Incident Number':fire_street_dict[key], 'Building Violation Number':0})

        repo['fire_building_transformation'].insert_many(new_combined_dataset)
        repo['fire_building_transformation'].metadata({'complete': True})
        print(repo['fire_building_transformation'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.


        this_script = doc.agent('alg:liweixi_mogujzhu#fire_building_transformation',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource_weather = doc.entity('dat:liweixi_mogujzhu#building_and_property_violations',
                              {'prov:label': 'Boston Building And Property Violations', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        resource_fire_incident = doc.entity('dat:liweixi_mogujzhu#fire_incident_report',
                              {'prov:label': 'Boston Fire Incident', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})

        get_weather_fire_incident_transformation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_weather_fire_incident_transformation, this_script)

        boston_fire_facility = doc.entity('dat:liweixi_mogujzhu#fire_building_transformation',
                          {prov.model.PROV_LABEL: 'Boston Building and Fire Incident', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(boston_fire_facility, this_script)
        doc.wasGeneratedBy(boston_fire_facility, get_weather_fire_incident_transformation, endTime)
        doc.wasDerivedFrom(boston_fire_facility, resource_fire_incident,
                           get_weather_fire_incident_transformation, get_weather_fire_incident_transformation,
                           get_weather_fire_incident_transformation)
        doc.wasDerivedFrom(boston_fire_facility, resource_weather,
                           get_weather_fire_incident_transformation, get_weather_fire_incident_transformation,
                           get_weather_fire_incident_transformation)

        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# fire_building_transormation.execute()
# doc = fire_building_transormation.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof
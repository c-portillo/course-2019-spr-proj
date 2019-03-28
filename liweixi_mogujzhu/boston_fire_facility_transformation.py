import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class boston_fire_facility_transformation(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = ['liweixi_mogujzhu.fire_hydrants','liweixi_mogujzhu.fire_department','liweixi_mogujzhu.fire_alarm_boxes']
    writes = ['liweixi_mogujzhu.boston_fire_facility_transformation']

    @staticmethod
    def merge_data(data_list, repo):
        '''
        :param data_list: The data list of mongodb as input
        :param repo: Mongodb repo
        :return: merged data which includes Boston Fire Hydrants, Fire Department, Fire Alarm Boxes
        with their coordinates and zipcode
        '''
        # geolocator = Nominatim(timeout=500)
        new_data = []
        for data in data_list:
            repo_data = repo[data]
            for row in repo_data.find():
                element = {}
                element['facility_type']= data[17:]
                element['coordinates'] = row['geometry']['coordinates'][::-1]
                # print(element['coordinates'])
                # location = geolocator.reverse(element['coordinates'])
                # print(location.raw)
                new_data.append(element)
        return new_data

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')
        repo.dropCollection("boston_fire_facility")
        repo.createCollection("boston_fire_facility")
        data_list = ["liweixi_mogujzhu.fire_hydrants","liweixi_mogujzhu.fire_department","liweixi_mogujzhu.fire_alarm_boxes"]
        data = boston_fire_facility_transformation.merge_data(data_list, repo)
        repo['liweixi_mogujzhu.boston_fire_facility'].insert_many(data)
        repo['liweixi_mogujzhu.boston_fire_facility'].metadata({'complete': True})
        print(repo['liweixi_mogujzhu.boston_fire_facility'].metadata())

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


        this_script = doc.agent('alg:liweixi_mogujzhu#boston_fire_facility_transformation',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource_fire_alarm_boxes = doc.entity('dat:liweixi_mogujzhu#fire_alarm_boxes',
                              {'prov:label': 'Boston Fire Alarm Boxes', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        resource_fire_department = doc.entity('dat:liweixi_mogujzhu#fire_department',
                              {'prov:label': 'Boston Fire Department', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        resource_fire_hydrants = doc.entity('dat:liweixi_mogujzhu#fire_hydrants',
                              {'prov:label': 'Boston Fire Hydrants', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        get_boston_fire_facility = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_boston_fire_facility, this_script)

        boston_fire_facility = doc.entity('dat:liweixi_mogujzhu#boston_fire_facility',
                          {prov.model.PROV_LABEL: 'Boston Fire Facility', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(boston_fire_facility, this_script)
        doc.wasGeneratedBy(boston_fire_facility, get_boston_fire_facility, endTime)
        doc.wasDerivedFrom(boston_fire_facility, resource_fire_department,
                           get_boston_fire_facility, get_boston_fire_facility, get_boston_fire_facility)
        doc.wasDerivedFrom(boston_fire_facility, resource_fire_alarm_boxes,
                           get_boston_fire_facility, get_boston_fire_facility, get_boston_fire_facility)
        doc.wasDerivedFrom(boston_fire_facility, resource_fire_hydrants,
                           get_boston_fire_facility, get_boston_fire_facility, get_boston_fire_facility)
        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# boston_fire_facility_transormation.execute()
# doc = boston_fire_facility_transormation.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof
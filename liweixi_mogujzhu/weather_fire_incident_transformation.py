import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class weather_fire_incident_transformation(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = ['liweixi_mogujzhu.weather','liweixi_mogujzhu.fire_incident_report']
    writes = ['liweixi_mogujzhu.weather_fire_incident_transformation']

    @staticmethod
    def merge_data(data_list, repo):
        '''
        :param data_list: The data list of mongodb as input
        :param repo: Mongodb repo
        :return: merged data which includes Boston daily weather condition as well as number of fire incident
        '''
        weather = repo[data_list[0]]
        incidents = repo[data_list[1]]
        new_data = []
        start_date =  datetime.datetime.strptime('2017-01-01', "%Y-%m-%d")
        end_date = datetime.datetime.strptime('2018-10-31',"%Y-%m-%d")
        date_dic = {}
        for incident in incidents.find():
            try:
                curr = datetime.datetime.strptime(incident['Alarm Date'], "%m/%d/%Y")
            except ValueError:
                curr = datetime.datetime.strptime(incident['Alarm Date'], "%m/%d/%y")
            except TypeError:
                pass
            if start_date<=curr<=end_date:
                if curr not in date_dic:
                    date_dic[curr]={'NINCIDENT':1, 'NLOSS':0}
                    if not incident['Estimated Property Loss']:
                        continue
                    elif incident['Estimated Property Loss']>0:
                        date_dic[curr]['NLOSS']+=1

                else:
                    date_dic[curr]['NINCIDENT']+=1
                    if not incident['Estimated Property Loss']:
                        continue
                    elif incident['Estimated Property Loss']>0:
                        date_dic[curr]['NLOSS']+=1
        for day in weather.find():
            curr = datetime.datetime.strptime(day['DATE'], "%Y-%m-%d")
            # Limit the date range within 2017-01-01 to 2018-10-31
            if start_date<=curr<=end_date:
                today = {}
                today['DATE'] = day['DATE']
                today['TMAX'] = day['TMAX']
                today['TMIN'] = day['TMIN']
                today['TAVG'] = day['TAVG']
                today['AWND'] = day['AWND']
                today['PRCP'] = day['PRCP']
                today['SNOW'] = day['SNOW']
                today['SNWD'] = day['SNWD']
                today['NINCIDENT'] = date_dic[curr]['NINCIDENT']
                today['NLOSS'] = date_dic[curr]['NLOSS']
                new_data.append(today)
        print(new_data[0])
        return new_data

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')
        repo.dropCollection("weather_fire_incident_transformation")
        repo.createCollection("weather_fire_incident_transformation")
        data_list = ['liweixi_mogujzhu.weather', 'liweixi_mogujzhu.fire_incident_report']
        data = weather_fire_incident_transformation.merge_data(data_list, repo)
        repo['weather_fire_incident_transformation'].insert_many(data)
        repo['weather_fire_incident_transformation'].metadata({'complete': True})
        print(repo['weather_fire_incident_transformation'].metadata())

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


        this_script = doc.agent('alg:liweixi_mogujzhu#weather_fire_incident_transormation',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource_weather = doc.entity('dat:liweixi_mogujzhu#weather',
                              {'prov:label': 'Boston Weather', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        resource_fire_incident = doc.entity('dat:liweixi_mogujzhu#fire_incident_report',
                              {'prov:label': 'Boston Fire Incident', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})

        get_weather_fire_incident_transformation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_weather_fire_incident_transformation, this_script)

        boston_fire_facility = doc.entity('dat:liweixi_mogujzhu#weather_fire_incident_transformation',
                          {prov.model.PROV_LABEL: 'Boston Weather and Fire Incident', prov.model.PROV_TYPE: 'ont:DataSet'})
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
# weather_fire_incident_transormation.execute()
# doc = weather_fire_incident_transormation.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import geocoder
from shapely.geometry import shape, Point


class serviceNeighborhood(dml.Algorithm):
    contributor = 'gasparde_ljmcgann'
    reads = ['gasparde_ljmcgann.services', 'gasparde_ljmcgann.neighborhoods']
    writes = ['gasparde_ljmcgann.service_grade']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')

        services = repo.gasparde_ljmcgann.services
        for service in services.find():
            print("hi!")
            lateness = datetime.datetime.strptime(service["closed_dt"],
                                                  "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(
                service["TARGET_DT"], "%Y-%m-%d %H:%M:%S")
            GeoLocation = (service["Latitude"], service["Longitude"])
            # print(repo.gasparde_ljmcgann.neighborhoods.find())
            neighBorhood = [neighborhood["Name"] for neighborhood in repo.gasparde_ljmcgann.neighborhoods.find() if
                            shape(neighborhood["geometry"]).contains(GeoLocation)]
            neighBorhood = neighBorhood[0]
            r = {"_id": service["_id"], "Lateness": lateness, "Neighborhood": service["neighborhood"],
                 "Neighborhood": neighBorhood, "GeoLocation": GeoLocation}
            repo.dropCollection("service_grade")
            repo.createCollection("service_grade")
            repo['gasparde_ljmcgann.service_grade'].insert_one(r)
            repo['gasparde_ljmcgann.service_grade'].metadata({'complete': True})
            print(repo['gasparde_ljmcgann.service_grade'].metadata())
            break

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
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:gasparde_ljmcgann#livingAreaCost',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_services = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_services, this_script)
        doc.wasAssociatedWith(get_services, this_script)
        doc.usage(get_services, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?$format=json'
                   }
                  )

        services = doc.entity('dat:gasparde_ljmcgann#services',
                              {prov.model.PROV_LABEL: 'Service Request in Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(services, this_script)
        doc.wasGeneratedBy(services, get_services, endTime)
        doc.wasDerivedFrom(services, resource, get_services, get_services, get_services)

        result = doc.entity('dat:gaspare_ljmcgann#service_grade', {prov.model.PROV_LABEL: 'The amount time the request is overdue'})
        doc.wasAttributedTo(services, this_script)
        doc.wasGeneratedBy(services, get_services, endTime)
        doc.wasDerivedFrom(result, resource, get_services, get_services, get_services)

        repo.logout()

        return doc


"""
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
if __name__ == '__main__':
    serviceNeighborhood.execute()
    doc = serviceNeighborhood.provenance()
    print(doc.get_provn())
    print(json.dumps(json.loads(doc.serialize()), indent=4))
"""
## eof

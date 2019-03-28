import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import geocoder


class livingAreaCost(dml.Algorithm):
    contributor = 'gasparde_ljmcgann'
    reads = ['gasparde_ljmcgann.properties']
    writes = ['gasparde_ljmcgann.property_assessment']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')

        # # 311 SERVICE REQUESTS
        props = repo.gasparde_ljmcgann.properties
        # print(props)
        for prop in props.find():
            print("hi!")
            _id = prop["_id"]
            address = prop["ST_NUM"].split(" ")[0] + " " + prop["ST_NAME"] + " " + prop[
                "ST_NAME_SUF"] + " BOSTON, MASSACHUSETTS " + \
                      prop["ZIPCODE"]

            ###################################################
            # geocode = geocoder.uscensus(address)            #
            # GeoLocation = geocode.latlng                    #
            ###################################################

            r = {"_id": _id, "AvgTotal": prop["AV_TOTAL"], "LivingArea": prop["LIVING_AREA"],
                 "GeoLocation": address}

            repo.dropCollection("property_assessment")
            repo.createCollection("property_assessment")
            repo['gasparde_ljmcgann.property_assessment'].insert_one(r)
            repo['gasparde_ljmcgann.property_assessment'].metadata({'complete': True})
            print(repo['gasparde_ljmcgann.property_assessment'].metadata())
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

        result = doc.entity('dat:gaspare_ljmcgann#property_assessment', {prov.model.PROV_LABEL: 'Price of Living Area'})
        doc.wasAttributedTo(services,this_script)
        doc.wasGeneratedBy(services,get_services,endTime)
        doc.wasDerivedFrom(result,resource,get_services,get_services,get_services)


        repo.logout()

        return doc


"""
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
if __name__ == '__main__':
    livingAreaCost.execute()
    doc = livingAreaCost.provenance()
    print(doc.get_provn())
    print(json.dumps(json.loads(doc.serialize()), indent=4))
"""
## eof

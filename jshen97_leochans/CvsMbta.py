import dml
import json
import prov.model
import pprint
import uuid
from math import sin, cos, sqrt, atan2, radians


class CvsMbta(dml.Algorithm):

    contributor = "jshen97_leochans"
    reads = ['jshen97_leochans.cvs',
             'jshen97_leochans.mbtaStops']
    writes = ['jshen97_leochans.cvsMBTA']

    @staticmethod
    def execute(trial=False):

        start_time = datetime.datetime.now()

        # set up database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('leochans_jshen97', 'leochans_jshen97')

        # create the result collections
        repo.dropCollection('cvsMBTA')
        repo.createCollection('cvsMBTA')
    

        # insert the geolocation, name, and google place_id
        for document in repo.jshen97_leochans.cvs.find():
            if 'results' in document.keys():
                for item in document['results']:
                    d = {
                        'name': 'CVS',
                        'location': item['geometry']['location'],
                        'place_id': item['place_id'],
                    }
                    repo['jshen97_leochans.cvsMBTA'].insert_one(d)
            else:
                continue

        # pick those MBTAs that are within 15 km of Boston and insert
        for document in repo.jshen97_leochans.mbtaStops.find():
            # R is the approximate radius of the earth in km
            # @see Haversine formula for latlng distance
            # All trig function in python use radian
            R = 6373.0

            lat_bos = 42.361145
            lng_bos = -71.057083

            lat = document['stop_lat']
            lng = document['stop_lon']

            dlon = lng_bos - lng
            dlat = lat_bos - lat
            a = sin(dlat / 2) ** 2 + cos(lat) * cos(lat_bos) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            if (distance < 15):
                d = {
                    'stop_id': document['stop_id'],
                    'location': [document['stop_lat'], document['stop_lon']],
     
                }
                repo['jshen97_leochans.cvsMBTA'].insert_one(d)
                
            else:
                continue

        # insert cvs within 15 km of boston
        for document in repo.jshen97_leochans.cvs.find():
            if 'results' in document.keys():
                for item in document['results']:
                    d = {
                        'name': 'CVS',
                        'location': item['geometry']['location'],
                        'place_id': item['place_id'],
                        'rating': item['rating'] if 'rating' in item.keys() else None,
                        'rating_count': item['user_ratings_total'] if 'user_ratings_total' in item.keys() else None
                    }
                    repo['jshen97_leochans.cvsMBTA'].insert_one(d)
            else:
                continue
            
        repo['jshen97_leochans.cvsMBTA'].metadata({'complete': True})
        print(repo['jshen97_leochans.cvsMBTA'].metadata())



        # check structure
        #for document in repo.jshen97_leochans.cvsMBTA.find():
        #    pprint.pprint(document)

        repo.logout()

        end_time = datetime.datetime.now()

        return {"start": start_time, "end": end_time}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), start_time=None, end_time=None):
        '''
        Create the provenance document describing everything happening
        in this script. Each run of the script will generate a new
        document describing that invocation event.
        '''

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('leochans_jshen97', 'leochans_jshen97')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:jshen97_leochans#cvsMBTA',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        
        resource_cvs = doc.entity('dat:cvs', {'prov:label': 'CVS Boston', prov.model.PROV_TYPE: 'ont:DataSet'})

        resource_mbta = doc.entity('dat:mbtaStops', {'prov:label': 'mbta stops', prov.model.PROV_TYPE: 'ont:DataSet'})
        
        combine_cvs = doc.activity('log:uuid' + str(uuid.uuid4()), start_time, end_time)
        combine_mbtaStops = doc.activity('log:uuid' + str(uuid.uuid4()), start_time, end_time)

        doc.wasAssociatedWith(combine_cvs, this_script)
        doc.usage(combine_cvs, resource_cvs, start_time, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(combine_cvs, resource_mbta, start_time, None, {prov.model.PROV_TYPE: 'ont:Computation'})


        cvsMBTA = doc.entity('dat:jshen97_leochans#cvsMBTA', {prov.model.PROV_LABEL: 'Combine CVS mbtaStops', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(cvsMBTA, this_script)
        doc.wasGeneratedBy(cvsMBTA, combine_cvs, end_time)
        doc.wasDerivedFrom(cvsMBTA, resource_cvs, combine_cvs, combine_cvs, combine_cvs)
        doc.wasDerivedFrom(cvsMBTA, resource_mbta, combine_cvs, combine_cvs, combine_cvs)

        return doc

# debug
'''
cvsMBTA.execute()
doc = cvsMBTA.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

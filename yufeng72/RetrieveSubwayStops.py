import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class RetrieveSubwayStops(dml.Algorithm):
    contributor = 'yufeng72'
    reads = []
    writes = ['yufeng72.subwayStops']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')

        url = 'http://datamechanics.io/data/yufeng72/Subway_Stops.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)

        repo.dropCollection("subwayStops")
        repo.createCollection("subwayStops")
        repo['yufeng72.subwayStops'].insert_many(r)
        repo['yufeng72.subwayStops'].metadata({'complete': True})
        print(repo['yufeng72.subwayStops'].metadata())

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
        repo.authenticate('yufeng72', 'yufeng72')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet',
        # 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/yufeng72/')

        this_script = doc.agent('alg:yufeng72#RetrieveSubwayStops',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('bdp:Subway_Stops',
                              {'prov:label': 'Subway Stops', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_subwayStops = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_subwayStops, this_script)
        doc.usage(get_subwayStops, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'select=stop_id,stop_name,stop_lat,stop_lon,location_type,wheelchair_boarding'
                   }
                  )

        subwayStops = doc.entity('dat:yufeng72#subwayStops',
                          {prov.model.PROV_LABEL: 'Subway Stops', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(subwayStops, this_script)
        doc.wasGeneratedBy(subwayStops, get_subwayStops, endTime)
        doc.wasDerivedFrom(subwayStops, resource, get_subwayStops, get_subwayStops, get_subwayStops)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
RetrieveSubwayStops.execute()
doc = RetrieveSubwayStops.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

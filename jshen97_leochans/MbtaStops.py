import dml
import datetime
import json
import math
import prov.model
import pprint
import uuid
from urllib.request import urlopen


class MbtaStops(dml.Algorithm):

    contributor = "jshen97_leochans"
    reads = []
    writes = ['jshen97_leochans.mbtaStops']

    @staticmethod
    def execute(trial=False):

        start_time = datetime.datetime.now()

        # set up database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('leochans_jshen97', 'leochans_jshen97')

        # retrieve MBTA stops
        url_mbtaStops = "http://datamechanics.io/data/MBTA_Stops.json"
        response_mbtaStops = json.loads(urlopen(url_mbtaStops).read().decode('utf-8'))
        res_dump_mbtaStops = json.dumps(response_mbtaStops, sort_keys=True, indent=2)
        repo.dropCollection('mbtaStops')
        repo.createCollection('mbtaStops')
       
        repo['jshen97_leochans.mbtaStops'].insert_one(response_mbtaStops)
        repo['jshen97_leochans.mbtaStops'].metadata({'complete': True})
        repo['jshen97_leochans.mbtaStops'].delete_many({'status': 'INVALID_REQUEST'})

        print(repo['jshen97_leochans.mbtaStops'].metadata())

        repo.logout()

        end_time = datetime.datetime.now()

        return {"start": start_time, "end": end_time}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), start_time=None, end_time=None):

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('leochans_jshen97', 'leochans_jshen97')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('dio', 'http://datamechanics.io/data/')

        this_script = doc.agent('alg:jshen97_leochans#mbtaStops',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        
        resource_dio = doc.entity('dio:wc8w-nujk', {'prov:label': 'Data Mechanics IO', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension':'json'})
        
        get_mbtaStops = doc.activity('log:uuid' + str(uuid.uuid4()), start_time, end_time)
        doc.wasAssociatedWith(get_mbtaStops, this_script)
        doc.usage(get_mbtaStops, resource_dio, start_time, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'MBTA_Stops.json'
                   }
                  )
        mbtaStops = doc.entity('dat:jshen97_leochans#mbtaStops',
                              {prov.model.PROV_LABEL: 'mbtaStops Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(mbtaStops, this_script)
        doc.wasGeneratedBy(mbtaStops, get_mbtaStops, end_time)
        doc.wasDerivedFrom(mbtaStops, resource_dio, get_mbtaStops, get_mbtaStops, get_mbtaStops)

        repo.logout()

        return doc

# debug
'''
MbtaStops.execute()
doc = MbtaStops.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

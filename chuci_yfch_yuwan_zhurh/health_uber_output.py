import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class health_uber_output(dml.Algorithm):
    contributor = 'chuci_yfch_yuwan_zhurh'
    reads = ['chuci_yfch_yuwan_zhurh.uber', 'chuci_yfch_yuwan_zhurh.health']
    writes = ['chuci_yfch_yuwan_zhurh.population', 'chuci_yfch_yuwan_zhurh.uber_mean', 'chuci_yfch_yuwan_zhurh.city_pop_time']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        # Get the uber dataset
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        # Aggreate cityname by max population
        pipline = [
            {'$group': {'_id': "$CityName", 'population': {'$max': "$PopulationCount"}}}
        ]
        agg_result = repo['chuci_yfch_yuwan_zhurh.health'].aggregate(pipline)
        agg_list = list(agg_result)
        repo.dropCollection("population")
        repo.createCollection("population")
        repo['chuci_yfch_yuwan_zhurh.population'].insert_many(agg_list)

        # Aggreate cityname by mean time

        pipline2 = [
            {'$group': {'_id': "$CITY", 'mean_time': {'$avg': "$Mean Travel Time (Seconds)"}}}
        ]
        agg_result_uber = repo['chuci_yfch_yuwan_zhurh.uber'].aggregate(pipline2)
        agg_list_uber = list(agg_result_uber)
        repo.dropCollection("uber_mean")
        repo.createCollection("uber_mean")
        repo['chuci_yfch_yuwan_zhurh.uber_mean'].insert_many(agg_list_uber)

        # use basic relation to join population and mean

        l1 = list(repo['chuci_yfch_yuwan_zhurh.population'].find())

        l2 = list(repo['chuci_yfch_yuwan_zhurh.uber_mean'].find())

        l3 = []
        for each1 in l1:
            for each2 in l2:
                if each1['_id'] == each2['_id']:
                    l3.append({'_id': each1['_id'],
                               'population': each1['population'],
                               'mean_time': each2['mean_time']
                               })
        repo.dropCollection("city_pop_time")
        repo.createCollection("city_pop_time")
        repo['chuci_yfch_yuwan_zhurh.city_pop_time'].insert_many(l3)

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
        # New
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        agent = doc.agent('alg:chuci_yfch_yuwan_zhurh#health_uber_output',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        entity_uber = doc.entity('dat:chuci_yfch_yuwan_zhurh#uber',
                           {prov.model.PROV_LABEL: 'uber data', prov.model.PROV_TYPE: 'ont:DataSet'})
        entity_health = doc.entity('dat:chuci_yfch_yuwan_zhurh#health',
                           {prov.model.PROV_LABEL: 'health data', prov.model.PROV_TYPE: 'ont:DataSet'})
        entity_result = doc.entity('dat:chuci_yfch_yuwan_zhurh#result',
                                   {prov.model.PROV_LABEL: 'result data', prov.model.PROV_TYPE: 'ont:DataSet'})
        activity = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(activity, agent)
        doc.usage(activity, entity_uber, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:aggregate'}
                  )
        doc.usage(activity, entity_health, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:aggregate'}
                  )
        doc.wasAttributedTo(entity_result, agent)
        doc.wasGeneratedBy(entity_result, activity, endTime)
        doc.wasDerivedFrom(entity_health, entity_result, activity, activity, activity)
        doc.wasDerivedFrom(entity_uber, entity_result, activity, activity, activity)

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
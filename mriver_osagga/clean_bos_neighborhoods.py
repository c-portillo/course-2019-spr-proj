import urllib.request
import json
import csv
import dml
import prov.model
import datetime
import uuid
from io import StringIO


class clean_bos_neighborhoods(dml.Algorithm):
    contributor = 'mriver_osagga'
    reads = ['mriver_osagga.bos_neighborhoods']
    writes = ['mriver_osagga.bos_neighborhoods_clean']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('mriver_osagga', 'mriver_osagga')

        data = list(repo['mriver_osagga.bos_neighborhoods'].find())
        # Projection to extract the neighborhoods list
        r_p = [{"Name": val['Name']} for val in data]
        r = json.loads(json.dumps(r_p))

        repo.dropCollection("bos_neighborhoods_clean")
        repo.createCollection("bos_neighborhoods_clean")
        repo['mriver_osagga.bos_neighborhoods_clean'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods_clean'].metadata(
            {'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods_clean'].metadata())

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
        repo.authenticate('mriver_osagga', 'mriver_osagga')
        # The scripts are in <folder>#<filename> format.
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        # The data sets are in <user>#<collection> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        # The event log.
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:mriver_osagga#clean_bos_neighborhoods', {
                                prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:boston_neighborhoods', {
                              'prov:label': 'Boston Neighborhoods', prov.model.PROV_TYPE: 'ont:DataSet'})
        clean_bos_neighborhoods = doc.activity(
            'log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(clean_bos_neighborhoods, this_script)
        doc.usage(clean_bos_neighborhoods, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Boston+Neighborhoods&$select=name'
                   }
                  )

        bos_neighborhoods_clean = doc.entity('dat:mriver_osagga#bos_neighborhoods_clean', {
                                             prov.model.PROV_LABEL: 'Boston Neighborhoods (Clean)', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(bos_neighborhoods_clean, this_script)
        doc.wasGeneratedBy(bos_neighborhoods_clean,
                           clean_bos_neighborhoods, endTime)
        doc.wasDerivedFrom(bos_neighborhoods_clean, resource,
                           clean_bos_neighborhoods, clean_bos_neighborhoods, clean_bos_neighborhoods)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
clean_bos_neighborhoods.execute()
doc = clean_bos_neighborhoods.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
# eof

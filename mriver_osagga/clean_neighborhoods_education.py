import urllib.request
import json
import csv
import dml
import prov.model
import datetime
import uuid
from io import StringIO


class clean_neighborhoods_education(dml.Algorithm):
    contributor = 'mriver_osagga'
    reads = ['mriver_osagga.bos_neighborhoods_education']
    writes = ['mriver_osagga.bos_neighborhoods_education_clean']

    @staticmethod
    def execute(trial=False):

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('mriver_osagga', 'mriver_osagga')

        data = list(repo['mriver_osagga.bos_neighborhoods_education'].find())

        # Selection and projection
        r = [{"Neighborhood": val['Neighborhood'], "Education Level": val['Education'],
              "Percent of Population": val['Percent of Population']} for val in data if (val['Decade'] == "2000")]
        r = json.loads(json.dumps(r))
        repo.dropCollection("bos_neighborhoods_education_clean")
        repo.createCollection("bos_neighborhoods_education_clean")
        repo['mriver_osagga.bos_neighborhoods_education_clean'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods_education_clean'].metadata({
                                                                         'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods_education_clean'].metadata())

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

        this_script = doc.agent('alg:mriver_osagga#clean_neighborhoods_education', {
                                prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:mriver_osagga#bos_neighborhoods_education', {
                              'prov:label': 'Boston Neighborhoods Education Attainment', prov.model.PROV_TYPE: 'ont:DataSet'})
        clean_neighborhoods_education = doc.activity(
            'log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(clean_neighborhoods_education, this_script)

        doc.usage(clean_neighborhoods_education, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Educational+attainment+demographics+by+neighborhood&$select=name'
                   }
                  )

        bos_neighborhoods_education_clean = doc.entity('dat:mriver_osagga#bos_neighborhoods_education_clean', {
                                                       prov.model.PROV_LABEL: 'Boston Neighborhoods Educational Attainment (Clean)', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(bos_neighborhoods_education_clean, this_script)
        doc.wasGeneratedBy(bos_neighborhoods_education_clean,
                           clean_neighborhoods_education, endTime)
        doc.wasDerivedFrom(bos_neighborhoods_education_clean, resource, clean_neighborhoods_education,
                           clean_neighborhoods_education, clean_neighborhoods_education)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
clean_neighborhoods_education.execute()
doc = clean_neighborhoods_education.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
# eof

import urllib.request
import json
import csv
import dml
import prov.model
import datetime
import uuid
from io import StringIO


class clean_neighborhoods_income(dml.Algorithm):
    contributor = 'mriver_osagga'
    reads = ['mriver_osagga.bos_neighborhoods_income']
    writes = ['mriver_osagga.clean_neighborhoods_ages_clean']

    @staticmethod
    def execute(trial=False):
        def add_entries(entries):
            total_population = sum([val["total_population"]
                                    for val in entries])
            total_low_income = sum([val["low_income"] for val in entries])
            return (total_population, total_low_income)

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('mriver_osagga', 'mriver_osagga')

        data = list(repo['mriver_osagga.bos_neighborhoods_income'].find())

        # projection to clean the data (remove excess col)
        R = [{"neighborhood": val['Name'], "low_income": int(
            val['Low_to_No']), "total_population": int(val['POP100_RE'])} for val in data]

        # aggregation (to sum up the total population per neighborhood)
        unique_neighborhoods = {r["neighborhood"] for r in R}
        r_a = [(neighborhood, add_entries([val for val in R if val["neighborhood"]
                                           == neighborhood])) for neighborhood in unique_neighborhoods]

        # projection to compute the low-income percentage per neighborhood
        r_p = [{"neighborhood": key, "low_income_percentage": val[1]/val[0]}
               for (key, val) in r_a]

        r = json.loads(json.dumps(r_p))

        repo.dropCollection("bos_neighborhoods_income_clean")
        repo.createCollection("bos_neighborhoods_income_clean")
        repo['mriver_osagga.bos_neighborhoods_income_clean'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods_income_clean'].metadata({
                                                                      'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods_income_clean'].metadata())

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

        this_script = doc.agent('alg:mriver_osagga#clean_neighborhoods_income', {
                                prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:mriver_osagga#bos_neighborhoods_income', {
                              'prov:label': 'Income by Neighborhood', prov.model.PROV_TYPE: 'ont:DataSet'})
        clean_neighborhoods_income = doc.activity(
            'log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(clean_neighborhoods_income, this_script)
        doc.usage(clean_neighborhoods_income, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Climate+Ready+Boston+Social+Vulnerability&$select=name'
                   }
                  )

        bos_neighborhoods_income_clean = doc.entity('dat:mriver_osagga#bos_neighborhoods_income_clean', {
                                                    prov.model.PROV_LABEL: 'Income by Neighborhood (Clean)', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(bos_neighborhoods_income_clean, this_script)
        doc.wasGeneratedBy(bos_neighborhoods_income_clean,
                           clean_neighborhoods_income, endTime)
        doc.wasDerivedFrom(bos_neighborhoods_income_clean, resource, clean_neighborhoods_income,
                           clean_neighborhoods_income, clean_neighborhoods_income)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
clean_neighborhoods_income.execute()
doc = clean_neighborhoods_income.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
# eof

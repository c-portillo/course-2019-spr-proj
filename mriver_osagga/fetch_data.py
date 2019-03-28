import urllib.request
import json
import csv
import dml
import prov.model
import datetime
import uuid
import ssl
from io import StringIO


class fetch_data(dml.Algorithm):
    contributor = 'mriver_osagga'
    reads = []
    writes = ['mriver_osagga.bos_neighborhoods', 'mriver_osagga.bos_neighborhoods_income',
              'mriver_osagga.bos_neighborhoods_ages', 'mriver_osagga.bos_neighborhoods_education', 'mriver_osagga.bos_311_reqs']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        context = ssl._create_unverified_context()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('mriver_osagga', 'mriver_osagga')

        # for the data set `bos_neighborhoods`
        url = 'http://opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.csv'
        response = urllib.request.urlopen(
            url, context=context).read().decode("utf-8")
        r = [json.loads(json.dumps(d))
             for d in csv.DictReader(StringIO(response))]
        repo.dropCollection("bos_neighborhoods")
        repo.createCollection("bos_neighborhoods")
        repo['mriver_osagga.bos_neighborhoods'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods'].metadata({'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods'].metadata())

        # for the data set `bos_neighborhoods_income`
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/34f2c48b670d4b43a617b1540f20efe3_0.csv'
        response = urllib.request.urlopen(
            url, context=context).read().decode("utf-8")
        r = [json.loads(json.dumps(d))
             for d in csv.DictReader(StringIO(response))]
        repo.dropCollection("bos_neighborhoods_income")
        repo.createCollection("bos_neighborhoods_income")
        repo['mriver_osagga.bos_neighborhoods_income'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods_income'].metadata(
            {'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods_income'].metadata())

        # for the data set `bos_neighborhoods_ages`
        url = 'http://data.boston.gov/dataset/8202abf2-8434-4934-959b-94643c7dac18/resource/c53f0204-3b39-4a33-8068-64168dbe9847/download/age.csv'
        response = urllib.request.urlopen(
            url, context=context).read().decode("utf-8")
        r = [json.loads(json.dumps(d))
             for d in csv.DictReader(StringIO(response))]
        repo.dropCollection("bos_neighborhoods_ages")
        repo.createCollection("bos_neighborhoods_ages")
        repo['mriver_osagga.bos_neighborhoods_ages'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods_ages'].metadata(
            {'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods_ages'].metadata())

        # for the data set `bos_neighborhoods_education`
        url = 'http://data.boston.gov/dataset/8202abf2-8434-4934-959b-94643c7dac18/resource/bb0f26f8-e472-483c-8f0c-e83048827673/download/educational-attainment-age-25.csv'
        response = urllib.request.urlopen(
            url, context=context).read().decode("utf-8")
        r = [json.loads(json.dumps(d))
             for d in csv.DictReader(StringIO(response))]
        repo.dropCollection("bos_neighborhoods_education")
        repo.createCollection("bos_neighborhoods_education")
        repo['mriver_osagga.bos_neighborhoods_education'].insert_many(r)
        repo['mriver_osagga.bos_neighborhoods_education'].metadata(
            {'complete': True})
        print(repo['mriver_osagga.bos_neighborhoods_education'].metadata())

        '''
        # for the data set `bos_311_reqs`
        url = 'http://data.boston.gov/dataset/8048697b-ad64-4bfc-b090-ee00169f2323/resource/2968e2c0-d479-49ba-a884-4ef523ada3c0/download/tmpnjyvx2w3.csv'
        response = urllib.request.urlopen(url, context=context).read().decode("utf-8")
        r = [json.loads(json.dumps(d))
             for d in csv.DictReader(StringIO(response))]
        repo.dropCollection("bos_311_reqs")
        repo.createCollection("bos_311_reqs")
        repo['mriver_osagga.bos_311_reqs'].insert_many(r)
        repo['mriver_osagga.bos_311_reqs'].metadata({'complete': True})
        print(repo['mriver_osagga.bos_311_reqs'].metadata())
        '''

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

        this_script = doc.agent('alg:mriver_osagga#fetch_data', {
                                prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource_1 = doc.entity('bdp:3525b0ee6e6b427f9aab5d0a1d0a1a28_0', {
                                'prov:label': 'Boston Neighborhoods', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        resource_2 = doc.entity('bdp:34f2c48b670d4b43a617b1540f20efe3_0.csv', {
                                'prov:label': 'Climate Ready Boston Social Vulnerability', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        resource_3 = doc.entity('bdp:age', {'prov:label': 'Age demographics by neighborhood',
                                            prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        resource_4 = doc.entity('bdp:educational-attainment-age-25', {
                                'prov:label': 'Educational attainment demographics by neighborhood', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
        # resource_5 = doc.entity('bdp:tmpnjyvx2w3', {
        # 'prov:label': '311 Service Requests', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})

        fetch_data = doc.activity(
            'log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(fetch_data, this_script)

        doc.usage(fetch_data, resource_1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Boston+Neighborhoods&$select=name'
                   }
                  )
        doc.usage(fetch_data, resource_2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Climate+Ready+Boston+Social+Vulnerability&$select=name'
                   }
                  )
        doc.usage(fetch_data, resource_3, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Age+demographics+by+neighborhood&$select=name'
                   }
                  )
        doc.usage(fetch_data, resource_4, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Educational+attainment+demographics+by+neighborhood&$select=name'
                   }
                  )
        # doc.usage(fetch_data, resource_5, startTime, None,
        #           {prov.model.PROV_TYPE: 'ont:Retrieval',
        #            'ont:Query': '?type=311+Service+Requests&$select=name'
        #            }
        #           )

        output_1 = doc.entity('dat:mriver_osagga#bos_neighborhoods', {
                              prov.model.PROV_LABEL: 'Boston Neighborhoods', prov.model.PROV_TYPE: 'ont:DataSet'})
        output_2 = doc.entity('dat:mriver_osagga#bos_neighborhoods_income', {
                              prov.model.PROV_LABEL: 'Income by Neighborhood', prov.model.PROV_TYPE: 'ont:DataSet'})
        output_3 = doc.entity('dat:mriver_osagga#bos_neighborhoods_ages', {
                              prov.model.PROV_LABEL: 'Age by Neighborhood', prov.model.PROV_TYPE: 'ont:DataSet'})
        output_4 = doc.entity('dat:mriver_osagga#bos_neighborhoods_education', {
                              prov.model.PROV_LABEL: 'Education by Neighborhood', prov.model.PROV_TYPE: 'ont:DataSet'})
        # output_5 = doc.entity('dat:mriver_osagga#bos_311_reqs', {
        #                       prov.model.PROV_LABEL: '311 Service Requests', prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(output_1, this_script)
        doc.wasAttributedTo(output_2, this_script)
        doc.wasAttributedTo(output_3, this_script)
        doc.wasAttributedTo(output_4, this_script)
        # doc.wasAttributedTo(output_5, this_script)

        doc.wasGeneratedBy(output_1, fetch_data, endTime)
        doc.wasGeneratedBy(output_2, fetch_data, endTime)
        doc.wasGeneratedBy(output_3, fetch_data, endTime)
        doc.wasGeneratedBy(output_4, fetch_data, endTime)
        # doc.wasGeneratedBy(output_5, fetch_data, endTime)

        doc.wasDerivedFrom(output_1, resource_1, fetch_data,
                           fetch_data, fetch_data)
        doc.wasDerivedFrom(output_2, resource_2, fetch_data,
                           fetch_data, fetch_data)
        doc.wasDerivedFrom(output_3, resource_3, fetch_data,
                           fetch_data, fetch_data)
        doc.wasDerivedFrom(output_4, resource_4, fetch_data,
                           fetch_data, fetch_data)
        # doc.wasDerivedFrom(output_5, resource_5, fetch_data,
        #                    fetch_data, fetch_data)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
fetch_data.execute()
doc = fetch_data.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
# eof

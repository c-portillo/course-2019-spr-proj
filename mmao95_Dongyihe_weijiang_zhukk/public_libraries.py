import pandas as pd
import requests
import json
import dml
import prov.model
import datetime
import uuid
import csv
from io import StringIO
import json
import pymongo
import math


class public_libraries(dml.Algorithm):
    # define relational models

    contributor = 'mmao95_Dongyihe_weijiang_zhukk'
    reads = []
    writes = [contributor + '.public_libraries']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()
        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        writes = [contributor + '.public_libraries']

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/cb00f9248aa6404ab741071ca3806c0e_6.csv'
        doc = requests.get(url).text
        data_file = StringIO(doc)
        reader = csv.reader(data_file)
        Public_Libraries_list = []
        for row in reader:
            Public_Libraries_list += [row]

        del Public_Libraries_list[0]

        def union(R, S):
            return R + S

        def difference(R, S):
            return [t for t in R if t not in S]

        def intersect(R, S):
            return [t for t in R if t in S]

        def project(R, p):
            return [p(t) for t in R]

        def select(R, s):
            return [t for t in R if s(t)]

        def product(R, S):
            return [(t, u) for t in R for u in S]

        def aggregate(R, f):
            keys = {r[0] for r in R}
            return [(key, f([v for (k, v) in R if k == key])) for key in keys]

        BSDZXYL = [(BRANCH, ST_ADDRESS, DISTRICT, ZIPCODE, X, Y, LIBRARIES) for [
            X, Y, OBJECTID_1, OBJECTID, LIBRARIES, DISTRICT, ST_ADDRESS, BRANCH, ZIPCODE] in Public_Libraries_list]

        columnName = ['Branch Name', 'Address', 'City',
                      'Zipcode', 'Latitude', 'Longitude', 'Numbers']
        df = pd.DataFrame(columns=columnName, data=BSDZXYL)
        data = json.loads(df.to_json(orient="records"))

        repo.dropCollection('public_libraries')
        repo.createCollection('public_libraries')
        repo[writes[0]].insert_many(data)

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

        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        # The scripts are in <folder>#<filename> format.
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        # The data sets are in <user>#<collection> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        # The event log.
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        doc.add_namespace('bdp', 'https://www.50states.com/bio/mass.htm')

        this_script = doc.agent('alg:' + contributor + '#public_libraries', {
                                prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label': '311, Service Requests',
                                                prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        get_names = doc.activity(
            'log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_names, this_script)
        doc.usage(get_names, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Computation': 'Data cleaning'
                   }
                  )

        fp = doc.entity('dat:' + contributor + '#public_libraries',
                        {prov.model.PROV_LABEL: 'Public Libraries', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fp, this_script)
        doc.wasGeneratedBy(fp, get_names, endTime)
        doc.wasDerivedFrom(fp, resource, get_names, get_names, get_names)

        repo.logout()

        return doc

# eof

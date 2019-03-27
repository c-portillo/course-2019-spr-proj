#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 17:46:24 2019

@author: zhukaikang
"""

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


class landmarks(dml.Algorithm):

    contributor = 'mmao95_Dongyihe_weijiang_zhukk'
    reads = []
    writes = [contributor + '.landmarks']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()
        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        writes = [contributor + '.landmarks']
        #url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.csv'

        # set up database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.csv'
        doc = requests.get(url).text
        # print(doc)
        data_file = StringIO(doc)
        reader = csv.reader(data_file)
        # print(reader)
        Landmarks = []
        for row in reader:
            Landmarks += [row]

        del Landmarks[0]

        Landmarks[71][7] = '74'
        for line in Landmarks:
            if(line[7] == '' or line[7] == ' '):
                line[7] = 0

        for line in Landmarks:
            if(line[9] == '' or line[9] == ' '):
                line[9] = None

        for line in Landmarks:
            if(line[11] == '' or line[11] == ' '):
                line[11] = None

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

        after_p = project(select(Landmarks, lambda t: float(t[7]) > 15), lambda t: (
            t[7], t[8], t[9], t[10], t[11], t[16], t[17]))
        after_pp = project(after_p, lambda t: (
            t[0], t[1], t[2], t[3], t[4], float(t[5]) // float(t[6])))
        column_names = ['Petition', 'Name of landmarks',
                        'Areas_Desi', 'Address', 'Neighbourhood', 'ShapeSTWidth']
        df = pd.DataFrame(columns=column_names, data=after_pp)
        data = json.loads(df.to_json(orient="records"))
        repo.dropCollection('landmarks')
        repo.createCollection('landmarks')
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
        doc.add_namespace(
            'bdp', 'https://data.boston.gov/dataset/boston-landmarks-commission-blc-landmarks')
        this_script = doc.agent('alg:' + contributor + '#landmarks', {
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

        fp = doc.entity('dat:' + contributor + '#landmarks',
                        {prov.model.PROV_LABEL: 'landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fp, this_script)
        doc.wasGeneratedBy(fp, get_names, endTime)
        doc.wasDerivedFrom(fp, resource, get_names, get_names, get_names)

        repo.logout()

        return doc

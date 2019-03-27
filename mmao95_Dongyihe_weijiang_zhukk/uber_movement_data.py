import urllib.request
import json
import dml
import pymongo
import prov.model
import datetime
import uuid
import pandas as pd


class uber_movement_data(dml.Algorithm):
	# define relational models
    contributor = 'mmao95_Dongyihe_weijiang_zhukk'
    reads = []
    writes = [contributor + '.uber_data',contributor + '.boston_censustracts',contributor + '.boston_traffic']

    @staticmethod
    def execute(trial=False):
        start_time = datetime.datetime.now()
        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        writes = [contributor + '.uber_data', contributor + '.boston_censustracts',contributor + '.boston_traffic']
        def aggregate(R, f):
            keys = {r[0] for r in R}
            return [(key, f([v for (k,v) in R if k == key])) for key in keys]
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)
        csv1 = pd.read_csv("http://datamechanics.io/data/boston-censustracts-2018-4-All-MonthlyAggregate.csv").values.tolist()
        csv2 = pd.read_csv("http://datamechanics.io/data/boston_censustracts.csv").values.tolist()
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


        l1 = [(s[0],1) for s in csv1]
        l2 = aggregate(l1,sum)
        l3 = [(s[1],s[2]) for s in csv2]
        l4 = project(select(product(l2,l3), lambda t :t[0][0]==t[1][0] ),lambda t: (t[1][1], t[0][1]))
        columnName = ['Street ID','Count']
        df = pd.DataFrame(columns=columnName, data=l2)
        repo.dropCollection('uber_data')
        repo.createCollection('uber_data')
        data = json.loads(df.to_json(orient="records"))
        repo[writes[0]].insert_many(data)
        repo[writes[0]].metadata({'complete': True})
        repo.dropCollection('boston_censustracts')
        repo.createCollection('boston_censustracts')
        columnName1 = ['Street ID','Street Name']
        df1 = pd.DataFrame(columns=columnName1, data=l3)
        data1 = json.loads(df1.to_json(orient="records"))
        repo[writes[1]].insert_many(data1)
        repo[writes[1]].metadata({'complete': True})
        repo.dropCollection('boston_traffic')
        repo.createCollection('boston_traffic')
        columnName2 = ['Street Name','Traffic Count']
        df2 = pd.DataFrame(columns=columnName1, data=l4)
        data2 = json.loads(df2.to_json(orient="records"))
        repo[writes[2]].insert_many(data2)
        repo[writes[2]].metadata({'complete': True})
        repo.logout()
        endtime = datetime.datetime.now()
        return {"start":start_time, "end":endtime}


    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://movement.uber.com/explore/boston/travel-times/query?lang=en-US')

        this_script = doc.agent('alg:' + contributor + '#uber_data',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_names = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_names, this_script)
        doc.usage(get_names, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Computation': 'Data cleaning'
                   }
                  )

        fp = doc.entity('dat:' + contributor + '#uber_data',
                        {prov.model.PROV_LABEL: 'Uber Data', prov.model.PROV_TYPE: 'ont:DataSet'})
        fp1 = doc.entity('dat:' + contributor + '#boston_censustracts',
                        {prov.model.PROV_LABEL: 'Boston Censustracts', prov.model.PROV_TYPE: 'ont:DataSet'})
        fp2 = doc.entity('dat:' + contributor + '#boston_traffic',
                        {prov.model.PROV_LABEL: 'Boston Traffic', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fp, this_script)
        doc.wasAttributedTo(fp1, this_script)
        doc.wasAttributedTo(fp2, this_script)
        doc.wasGeneratedBy(fp, get_names, endTime)
        doc.wasGeneratedBy(fp1, get_names, endTime)
        doc.wasGeneratedBy(fp2, get_names, endTime)
        doc.wasDerivedFrom(fp, resource, get_names, get_names, get_names)
        doc.wasDerivedFrom(fp1, resource, get_names, get_names, get_names)
        doc.wasDerivedFrom(fp2, fp1, get_names, get_names, get_names)

        repo.logout()

        return doc

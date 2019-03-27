import prov.model
import dml
import datetime
import uuid
import json
import pandas as koalas
import pymongo


def union(R, S):
    return R + S


def project(R, p):
    return [p(t) for t in R]


def select(R, s):
    return [t for t in R if s(t)]


def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k, v) in R if k == key])) for key in keys]


def selector(data):
    values = []
    for i in range(3, len(data)):
        values.append(int((str(data[i])).replace(',', '')))
    return [data[0], tuple(values)]


def multipleSums(data):
    sums = [0] * len(data[0])
    for j in range(0, len(data[0])):
        for i in range(0, len(data)):
            sums[j] += data[i][j]
    return sums


def multipleAverages(data):
    avgs = [0.0] * len(data[0])
    for j in range(0, len(data[0])):
        for i in range(0, len(data)):
            avgs[j] += data[i][j]
        avgs[j] = avgs[j] / len(data)
    return avgs


def unzipper(data):
    res = [data[0]]
    for dat in data[1]:
        res.append(dat)
    return res


class questionsAggr(dml.Algorithm):
    contributor = 'stathisk_simonwu_nathanmo_nikm'
    reads = ['stathisk_simonwu_nathanmo_nikm.q1', 'stathisk_simonwu_nathanmo_nikm.q2', 'stathisk_simonwu_nathanmo_nikm.q3', 'stathisk_simonwu_nathanmo_nikm.q4']
    writes = ['stathisk_simonwu_nathanmo_nikm.avgAnswers']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        dml.pymongo.MongoClient()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')

        urls = ['stathisk_simonwu_nathanmo_nikm.q1', 'stathisk_simonwu_nathanmo_nikm.q2', 'stathisk_simonwu_nathanmo_nikm.q3', 'stathisk_simonwu_nathanmo_nikm.q4']
        combined = []
        for url in urls:
            df = list((repo[url].find()))
            df = koalas.DataFrame(df)
            df = df[['Locality', 'Ward', 'Pct', 'Yes', 'No', 'Blanks', 'Total Votes Cast']]

            res = aggregate(project(df.values[0:len(df.values) - 1], selector), multipleSums)
            combined = union(combined, res)
        final = koalas.DataFrame(data=project(aggregate(combined, multipleAverages), unzipper),
                                 columns=['Locality', 'Yes', 'No', 'Blanks', 'Total Votes Cast'])
        repo['avgAnswers'].insert_many(json.loads(final.to_json(orient='records')))
        repo['avgAnswers'].metadata({'complete': True})

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
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:stathisk_simonwu_nathanmo_nikm#questionsAggr',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        q1 = doc.entity('dat:question1',
                        {'prov:label': 'ballot question 1', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})

        q2 = doc.entity('dat:question2',
                        {'prov:label': 'ballot question 2', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})

        q3 = doc.entity('dat:question3',
                        {'prov:label': 'ballot question 3', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})

        q4 = doc.entity('dat:question4',
                        {'prov:label': 'ballot question 4', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})
        f = doc.entity('dat:question4',
                        {'prov:label': 'ballot question 4', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})

        get_q1 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_q2 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_q3 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_q4 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        get_final = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_q1, this_script)
        doc.wasAssociatedWith(get_q2, this_script)
        doc.wasAssociatedWith(get_q3, this_script)
        doc.wasAssociatedWith(get_q4, this_script)
        doc.wasAssociatedWith(get_final, this_script)

        doc.usage(get_q1, q1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_q1, q2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_q1, q3, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_q1, q4, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        doc.usage(get_final, f, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        final_stats = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#avgAnswers',
                                 {prov.model.PROV_LABEL: 'avg answers for ballot questions 2016',
                                  prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(final_stats, this_script)
        doc.wasGeneratedBy(final_stats, get_final, endTime)
        doc.wasDerivedFrom(final_stats, q1, q1, q3, q4)

        repo.logout()
        return doc


questionsAggr.execute()
doc = questionsAggr.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
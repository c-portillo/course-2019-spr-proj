import json
import dml
import prov.model
import datetime
import uuid
import math
import random

class cluster_status(dml.Algorithm):
    contributor = 'ojhamb_runtongy_sgullett_zybu'
    reads = ['ojhamb_runtongy_sgullett_zybu.student_status']
    writes = ['ojhamb_runtongy_sgullett_zybu.cluster_status']
    @staticmethod
    def execute(trial=False):
        def dist(p,q):
            (b1,c1,d1,f1)=p
            (b2,c2,d2,f2)=q
            # return abs(b1-b2) + abs(c1-c2) + abs(d1-d2) + abs(f1-f2)
            return (b1-b2)**2 + (c1-c2)**2 + (d1-d2)**2 + (f1-f2)**2
        def product(R, S):
            return [(t,u) for t in R for u in S]
        def aggregate(R, f):
            keys = {r[0] for r in R}
            return [(key, f([v for (k,v) in R if k == key])) for key in keys]
        def scale(p,x):
            (a,b,c,d) = p
            return (a//x,b//x,c//x,d//x)
        def plus(args):
            p = [0,0,0,0]
            for (a,b,c,d) in args:
                p[0]+=a
                p[1]+=b
                p[2]+=c
                p[3]+=d
            return tuple(p)
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')

        repo.dropCollection("cluster_status")
        repo.createCollection("cluster_status")
        rndid = []
        i = 0
        for i in range(4):
            rndid.append(random.randint(1,481))
        M = [(int(x["AnnouncementsView"]),int(x["Discussion"]),int(x["VisITedResources"]),int(x["raisedhands"])) for x in repo.ojhamb_runtongy_sgullett_zybu.student_status.find() if int(x["ID"]) in rndid]

        P = [(int(x["AnnouncementsView"]),int(x["Discussion"]),int(x["VisITedResources"]),int(x["raisedhands"])) for x in repo.ojhamb_runtongy_sgullett_zybu.student_status.find()]

        OLD = []
        while OLD != M:
            OLD = M

            MPD = [(m, p, dist(m,p)) for (m, p) in product(M, P)]
            PDs = [(p, dist(m,p)) for (m, p, d) in MPD]
            PD = aggregate(PDs, min)
            MP = [(m, p) for ((m,p,d), (p2,d2)) in product(MPD, PD) if p==p2 and d==d2]
            MT = aggregate(MP, plus)

            M1 = [(m, 1) for (m, _) in MP]
            MC = aggregate(M1, sum)

            M = [scale(t,c) for ((m,t),(m2,c)) in product(MT, MC) if m == m2]
            print(sorted(M))

        cluster = []

        for x in M:
            cluster.append({"AnnouncementsView": x[0], "Discussion": x[1], "VisITedResources": x[2], "raisedhands": x[3]})

        repo['ojhamb_runtongy_sgullett_zybu.cluster_status'].insert_many(cluster)
        repo['ojhamb_runtongy_sgullett_zybu.cluster_status'].metadata({'complete': True})
        print(repo['ojhamb_runtongy_sgullett_zybu.cluster_status'].metadata())

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
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu#cluster_status',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        student_status = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#student_status',
                              {'prov:label': 'Cluster_Status', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_clu_status = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_clu_status, this_script)

        doc.usage(get_clu_status, student_status, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        cluster_status = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#cluster_status',
                          {prov.model.PROV_LABEL: 'Cluster Status', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(cluster_status, this_script)
        doc.wasGeneratedBy(cluster_status, get_clu_status, endTime)
        doc.wasDerivedFrom(cluster_status, student_status, get_clu_status, get_clu_status, get_clu_status)


        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
cluster_status.execute()
doc = cluster_status.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof


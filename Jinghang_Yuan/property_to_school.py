import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class property_to_school(dml.Algorithm):
    contributor = 'Jinghang_Yuan'
    reads = ['Jinghang_Yuan.property','Jinghang_Yuan.school']
    writes = ['Jinghang_Yuan.property_to_school']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')

        def select(R, s):
            return [t for t in R if s(t)]

        def product(R, S):
            return [(t, u) for t in R for u in S]

        def project(R, p):
            return [p(t) for t in R]

        # projection of property,
        X = list(repo['Jinghang_Yuan.property'].find({}, {'_id':0,'PID':1,'MAIL_ZIPCODE': 1}))
        # print(list(repo['Jinghang_Yuan.property'].find({}, {'_id':0,'PID':1,'MAIL_ZIPCODE': 1})))

        # projection of school
        Y = list(repo['Jinghang_Yuan.school'].find({}, {'_id':0,'SCHID':1,'ZIP':1}))
        # print(list(repo['Jinghang_Yuan.school'].find({}, {'_id':0,'SCHID':1,'ZIP':1})))

        #join of property and school
        M = select(product(X, Y), lambda t: t[0]['MAIL_ZIPCODE'] == t[1]['ZIP'])
        RESULT = project(M, lambda t: {'ZIP': t[0]['MAIL_ZIPCODE'], 'PID': t[0]['PID'],
                                    'SCHID': t[1]['SCHID']})

        repo.dropCollection("property_to_school")
        repo.createCollection("property_to_school")
        repo["Jinghang_Yuan.property_to_school"].insert_many(RESULT)

        # print(list(repo["Jinghang_Yuan.property_to_school"].find()))

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('Jinghang_Yuan', 'Jinghang_Yuan')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        #doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')


        this_script = doc.agent('alg:Jinghang_Yuan#property_to_school', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        property = doc.entity('dat:Jinghang_Yuan#property',
                           {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        school = doc.entity('dat:Jinghang_Yuan#school',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})
        property_school_by_zip = doc.entity('dat:Jinghang_Yuan#property_school_by_zip',
                               {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                                'ont:Extension': 'json'})

        ppty_scl_join_by_zip = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(ppty_scl_join_by_zip, this_script)

        doc.usage(ppty_scl_join_by_zip, school, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.usage(ppty_scl_join_by_zip, property, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})

       
        doc.wasAttributedTo(property_school_by_zip, this_script)
        #doc.wasAttributedTo(citycrime, this_script)
        doc.wasGeneratedBy(property_school_by_zip, ppty_scl_join_by_zip, endTime)

        doc.wasDerivedFrom(school, property_school_by_zip, ppty_scl_join_by_zip, ppty_scl_join_by_zip, ppty_scl_join_by_zip)
        doc.wasDerivedFrom(property, property_school_by_zip, ppty_scl_join_by_zip, ppty_scl_join_by_zip, ppty_scl_join_by_zip)

        repo.logout()

        return doc


property_to_school.execute()
# # doc = school_to_property.provenance()
# # print(doc.get_provn())
# # print(json.dumps(json.loads(doc.serialize()), indent=4))

##eof
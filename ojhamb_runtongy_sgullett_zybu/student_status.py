import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class student_status(dml.Algorithm):
    contributor = 'ojhamb_runtongy_sgullett_zybu'
    reads = []
    writes = ['ojhamb_runtongy_sgullett_zybu.student_status']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')

        url = 'http://datamechanics.io/data/Jordan_Student_Status.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("student_status")
        repo.createCollection("student_status")
        repo['ojhamb_runtongy_sgullett_zybu.student_status'].insert_many(r)
        repo['ojhamb_runtongy_sgullett_zybu.student_status'].metadata({'complete':True})
        print(repo['ojhamb_runtongy_sgullett_zybu'].metadata())

        # url = 'http://cs-people.bu.edu/lapets/591/examples/found.json'
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        # r = json.loads(response)
        # s = json.dumps(r, sort_keys=True, indent=2)
        # repo.dropCollection("found")
        # repo.createCollection("found")
        # repo['alice_bob.found'].insert_many(r)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        #doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:student_status', {'prov:label':'student_status_inclass', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_stu_status = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        #get_lost = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stu_status, this_script)
        #doc.wasAssociatedWith(get_lost, this_script)
        doc.usage(get_stu_status, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'}
                  )
        # doc.usage(get_lost, resource, startTime, None,
        #           {prov.model.PROV_TYPE:'ont:Retrieval',
        #           'ont:Query':'?type=Animal+Lost&$select=type,latitude,longitude,OPEN_DT'
        #           }
        #           )

        stu_status = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#student_status', {prov.model.PROV_LABEL:'stu_status', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(stu_status, this_script)
        doc.wasGeneratedBy(stu_status, get_stu_status, endTime)
        doc.wasDerivedFrom(stu_status, resource, get_stu_status, get_stu_status, get_stu_status)

        # found = doc.entity('dat:alice_bob#found', {prov.model.PROV_LABEL:'Animals Found', prov.model.PROV_TYPE:'ont:DataSet'})
        # doc.wasAttributedTo(found, this_script)
        # doc.wasGeneratedBy(found, get_found, endTime)
        # doc.wasDerivedFrom(found, resource, get_found, get_found, get_found)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
student_status.execute()
doc = student_status.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof

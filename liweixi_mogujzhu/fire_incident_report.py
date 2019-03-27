import urllib.request
import requests
import pandas as pd
import json
import dml
import prov.model
import datetime
import uuid
import io
import csv


url = ['https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/220a4ce5-a991-4336-a19b-159881d7c2e7/download/october.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/5cd71efe-77ea-48a0-bc4e-92686db26d50/download/september.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/2eb323d1-0df0-4e56-8496-e5c8588f667a/download/august.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/950a6113-b1a8-4e11-8e7e-93a1784e9906/download/july.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/06fcfff1-993f-461a-9d69-c38f6bc103c9/download/june.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/9a3021d0-19d5-4522-9c69-7fdb9fc60ecf/download/may.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/8eebb3ef-c656-4c5e-b5c4-e5484e387533/download/april.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/70c463da-80ec-4d40-8273-aa8d0f695095/download/march.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/8424cc7d-2592-4b82-94e7-6ac28488f80f/download/february.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/0511abbd-d94f-49e9-b596-1e87b35a2ce8/download/january.2018-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/8f4f497e-d93c-4f2f-b754-bfc69e2700a0/download/december.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/d969a70d-2734-4e75-b2ae-e64aec289892/download/november.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/8608b9db-71e2-4acb-9691-75b3c66fdd17/download/october.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/14683ec2-c53a-46e0-b6de-67ec123629f0/download/september.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/9f27c0f7-c1a5-4ce3-8e68-52c32df47fd4/download/august.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/32cced02-0939-4a30-8c16-4708df591a86/download/july.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/755c4739-3ffc-4b71-aed2-40eb47256cb4/download/june.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/9d91dbc7-9875-4cd9-a772-3b363a4b193f/download/may.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/966caaf1-ecbc-4e91-8407-22e6cab7594a/download/april.2017-bostonfireincidentopendata.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/418bb785-5d50-428c-a445-d9635434ba62/download/march.2017-bostonfireincidents.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/0f59c8e6-e028-4dba-a6aa-87bd3304c766/download/february.2017-bostonfireincidents-2.csv', 'https://data.boston.gov/dataset/ac9e373a-1303-4563-b28e-29070229fdfe/resource/ce5cb864-bd01-4707-b381-9e204b4db73f/download/january.2017-bostonfireincidents-1.csv']


def getUrlList():
    return url


class fire_incident_report(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = []
    writes = ['liweixi_mogujzhu.fire_incident_report']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        print('getting fire incident report...')
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')

        urls = getUrlList()
        repo.dropCollection("fire_incident_report")
        repo.createCollection("fire_incident_report")
        for url in urls:
            fire_incident = pd.read_csv(url)
            fire_incident = json.loads(fire_incident.to_json(orient='records'))
            # print(fire_incident[:1])
            # s = json.dumps(r, sort_keys=True, indent=2)
            repo['liweixi_mogujzhu.fire_incident_report'].insert_many(fire_incident)
            repo['liweixi_mogujzhu.fire_incident_report'].metadata({'complete': True})
            print(repo['liweixi_mogujzhu.fire_incident_report'].metadata())

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
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.boston.gov/dataset/fire-incident-reporting')

        this_script = doc.agent('alg:liweixi_mogujzhu#fire_incident_report',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:liweixi_mogujzhu#fire_incident_report',
                              {'prov:label': 'Boston Fire Incident', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_fire_incident_report = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fire_incident_report, this_script)
        doc.usage(get_fire_incident_report, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'
                   }
                  )

        fire_incident_report = doc.entity('dat:liweixi_mogujzhu#fire_incident_report',
                          {prov.model.PROV_LABEL: 'Boston Fire Incident', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fire_incident_report, this_script)
        doc.wasGeneratedBy(fire_incident_report, get_fire_incident_report, endTime)
        doc.wasDerivedFrom(fire_incident_report, resource, get_fire_incident_report, get_fire_incident_report, get_fire_incident_report)

        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# fire_incident_report.execute()
# doc = fire_incident_report.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof
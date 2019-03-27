"""
CS504 : countyShapes
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : retrieval of county geoJSON data

Notes :

February 26, 2019
"""

import csv
import datetime
import io
import json
import uuid

import dml
import prov.model
import urllib.request

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, FUSION_TABLE_URL, COUNTY_SHAPE, COUNTY_SHAPE_NAME


class countyShapes(dml.Algorithm):
    contributor = TEAM_NAME
    reads = []
    writes = [COUNTY_SHAPE_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Read from Google Fusion table (uploaded to datamechanics.io)
            to get geoJSON data about each county
            and insert into collection
            ex) {
                    "_id" : "7322",
                    "Name" : Barnstable,
                    "Shape" : "<Polygon> ... ",
                    "Geo_ID" : "25001",
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        url = FUSION_TABLE_URL

        csv_string = urllib.request.urlopen(url).read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_string))
        response = json.loads(json.dumps(list(reader)))

        new_list = []

        for county in response:
            new_json = {}
            new_json['Name'] = county['County Name']
            new_json['Shape'] = county['geometry']
            new_json['Geo_ID'] = county['GEO_ID2']
            new_list += [new_json]

        repo.dropCollection(COUNTY_SHAPE)
        repo.createCollection(COUNTY_SHAPE)
        repo[COUNTY_SHAPE_NAME].insert_many(new_list)
        repo[COUNTY_SHAPE_NAME].metadata({'complete': True})
        print(repo[COUNTY_SHAPE_NAME].metadata())

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
        repo.authenticate(TEAM_NAME, TEAM_NAME)
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('shapes', 'http://datamechanics.io/data/') # Source for getting the counties' shape-point data

        this_script = doc.agent('alg:ldisalvo_skeesara_vidyaap#countyShapes',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('shapes:ldisalvo_skeesara_vidyaap/',
                              {'prov:label': 'County Shapes Points', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_shape = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_shape, this_script)
        doc.usage(get_shape, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'massachusetts_counties.csv'
                   }
                  )

        shapes = doc.entity('dat:ldisalvo_skeesara_vidyaap#countyShape',
                          {prov.model.PROV_LABEL: 'Shape Data for Each County', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(shapes, this_script)
        doc.wasGeneratedBy(shapes, get_shape, endTime)
        doc.wasDerivedFrom(shapes, resource, get_shape, get_shape, get_shape)

        repo.logout()

        return doc


'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
## eof
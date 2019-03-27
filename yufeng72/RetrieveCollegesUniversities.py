import csv
import io
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class RetrieveCollegesUniversities(dml.Algorithm):
    contributor = 'yufeng72'
    reads = []
    writes = ['yufeng72.collegesUniversities']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')

        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/cbf14bb032ef4bd38e20429f71acb61a_2.csv'
        response = urllib.request.urlopen(url)
        r = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter=',')
        r_parse = []
        for row in r:
            temp = {'OBJECTID': row[0], 'Match_type': row[1], 'Ref_ID': row[2], 'ID1': row[3], 'Id': row[4],
                    'SchoolId': row[5], 'Name': row[6], 'Address': row[7], 'City': row[8], 'Zipcode': row[9],
                    'Contact': row[10], 'PhoneNumbe': row[11], 'YearBuilt': row[12], 'NumStories': row[13],
                    'Cost': row[14], 'NumStudent': row[15], 'BackupPowe': row[16], 'ShelterCap': row[17],
                    'Latitude': row[18], 'Longitude': row[19], 'Comment': row[20], 'X': row[21], 'Y': row[22],
                    'NumStudents12': row[23], 'CampusHous': row[24], 'NumStudents13': row[25], 'URL': row[26]}
            r_parse.append(temp)
        r_parse.remove(r_parse[0])

        repo.dropCollection("collegesUniversities")
        repo.createCollection("collegesUniversities")
        repo['yufeng72.collegesUniversities'].insert_many(r_parse)
        repo['yufeng72.collegesUniversities'].metadata({'complete': True})
        print(repo['yufeng72.collegesUniversities'].metadata())

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
        repo.authenticate('yufeng72', 'yufeng72')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet',
        # 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:yufeng72#RetrieveCollegesUniversities',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('bdp:cbf14bb032ef4bd38e20429f71acb61a_2',
                              {'prov:label': 'Colleges and Universities', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})

        get_collegesUniversities = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_collegesUniversities, this_script)
        doc.usage(get_collegesUniversities, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?Ref_ID=0&$select=Ref_ID,Latitude,Longitude,Address,City,Schoold,Name,...'
                   }
                  )

        collegesUniversities = doc.entity('dat:yufeng72#collegesUniversities',
                          {prov.model.PROV_LABEL: 'Colleges and Universities', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(collegesUniversities, this_script)
        doc.wasGeneratedBy(collegesUniversities, get_collegesUniversities, endTime)
        doc.wasDerivedFrom(collegesUniversities, resource, get_collegesUniversities, get_collegesUniversities,
                           get_collegesUniversities)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
RetrieveCollegesUniversities.execute()
doc = RetrieveCollegesUniversities.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

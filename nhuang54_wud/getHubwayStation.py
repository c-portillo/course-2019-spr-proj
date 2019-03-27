import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

def csv_to_json(url):
    file = urllib.request.urlopen(url).read().decode("utf-8")  # retrieve file from datamechanics.io
    dict_values = []
    entries = file.split('\n')

    keys = entries[0].split(',')  # retrieve column names for keys

    for r in entries[1:-1]:
        val = r.split(',')
        val[-1] = val[-1][:-1]
        dictionary = dict([(keys[i], val[i]) for i in range(len(keys))])
        dict_values.append(dictionary)
    return dict_values

class getHubwayStation(dml.Algorithm):
    contributor = 'nhuang54_wud'
    reads = []
    writes = ['nhuang54_wud.hubwayStation']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')

        # Get Traffic Signals csv data in area of Boston
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/ee7474e2a0aa45cbbdfe0b747a5eb032_0.csv'
        json_file = csv_to_json(url)

        # Store in DB
        repo.dropCollection("hubwayStation")
        repo.createCollection("hubwayStation")
        repo['nhuang54_wud.hubwayStation'].insert_many(json_file)
        repo['nhuang54_wud.hubwayStation'].metadata({'complete':True})
        print(repo['nhuang54_wud.hubwayStation'].metadata())

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
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        # Resource:
        doc.add_namespace('bod', 'https://opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:nhuang54_wud#hubwayStation', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bod:ee7474e2a0aa45cbbdfe0b747a5eb032_0', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_hubwayStation = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_hubwayStation, this_script)

        doc.usage(get_hubwayStation, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        hubwayStation = doc.entity('dat:nhuang54_wud#hubwayStation', {prov.model.PROV_LABEL:'Hubway Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(hubwayStation, this_script)
        doc.wasGeneratedBy(hubwayStation, get_hubwayStation, endTime)
        doc.wasDerivedFrom(hubwayStation, resource, get_hubwayStation, get_hubwayStation, get_hubwayStation)

        repo.logout()

        return doc

##example.execute()
##doc = example.provenance()
##print(doc.get_provn())
##print(json.dumps(json.loads(doc.serialize()), indent=4))
if __name__ == '__main__':
    getHubwayStation.execute()

## eof

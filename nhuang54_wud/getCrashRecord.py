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

class getCrashRecord(dml.Algorithm):
    contributor = 'nhuang54_wud'
    reads = []
    writes = ['nhuang54_wud.crashRecord']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')

        # get the csv file from website and turn into json object
        url = 'https://data.boston.gov/dataset/7b29c1b2-7ec2-4023-8292-c24f5d8f0905/resource/e4bfe397-6bfc-49c5-9367-c879fac7401d/download/crash_open_data.csv'
        json_file = csv_to_json(url)

        # Store in DB
        repo.dropCollection("crashRecord")
        repo.createCollection("crashRecord")
        repo['nhuang54_wud.crashRecord'].insert_many(json_file)
        repo['nhuang54_wud.crashRecord'].metadata({'complete':True})
        print(repo['nhuang54_wud.crashRecord'].metadata())

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
        doc.add_namespace('bdp', 'https://data.boston.gov/dataset/')

        this_script = doc.agent('alg:nhuang54_wud#getCrashSignal', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:7b29c1b2-7ec2-4023-8292-c24f5d8f0905/resource/e4bfe397-6bfc-49c5-9367-c879fac7401d/download/crash_open_data', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_crashRecord = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_crashRecord, this_script)

        doc.usage(get_crashRecord, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        crashRecord = doc.entity('dat:nhuang54_wud#crashRecord', {prov.model.PROV_LABEL:'Crash Records', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crashRecord, this_script)
        doc.wasGeneratedBy(crashRecord, get_crashRecord, endTime)
        doc.wasDerivedFrom(crashRecord, resource, get_crashRecord, get_crashRecord, get_crashRecord)

        repo.logout()

        return doc

##example.execute()
##doc = example.provenance()
##print(doc.get_provn())
##print(json.dumps(json.loads(doc.serialize()), indent=4))
if __name__ == '__main__':
    getCrashRecord.execute()

## eof

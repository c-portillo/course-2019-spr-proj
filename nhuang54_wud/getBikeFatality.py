import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

# method to convert csv into json, returns dictionary
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


class getBikeFatality(dml.Algorithm):
    contributor = 'nhuang54_wud'
    reads = []
    writes = ['nhuang54_wud.bikeFatality']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')

        url = 'https://data.boston.gov/dataset/d326a4e3-75f2-42ac-9b32-e2920566d04c/resource/92f18923-d4ec-4c17-9405-4e0da63e1d6c/download/fatality_open_data.csv'
        json_file = csv_to_json(url)
        
        repo.dropCollection("bikeFatality")
        repo.createCollection("bikeFatality")
        repo['nhuang54_wud.bikeFatality'].insert_many(json_file)
        repo['nhuang54_wud.bikeFatality'].metadata({'complete':True})
        print(repo['nhuang54_wud.bikeFatality'].metadata())

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

        # https://data.boston.gov/dataset/d326a4e3-75f2-42ac-9b32-e2920566d04c/resource/92f18923-d4ec-4c17-9405-4e0da63e1d6c/download/fatality_open_data.csv
        this_script = doc.agent('alg:nhuang54_wud#getBikeFatality', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:d326a4e3-75f2-42ac-9b32-e2920566d04c/resource/92f18923-d4ec-4c17-9405-4e0da63e1d6c/download/fatality_open_data', {'prov:label':'Vision Zero Fatality Records', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_bikeFatality = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_bikeFatality, this_script)
        doc.usage(get_bikeFatality, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        bikeFatality = doc.entity('dat:nhuang54_wud#bikeFatality', {prov.model.PROV_LABEL:'Vision Zero Fatality Records', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bikeFatality, this_script)
        doc.wasGeneratedBy(bikeFatality, get_bikeFatality, endTime)
        doc.wasDerivedFrom(bikeFatality, resource, get_bikeFatality, get_bikeFatality, get_bikeFatality)


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

if __name__ == '__main__':
    getBikeFatality.execute()

## eof

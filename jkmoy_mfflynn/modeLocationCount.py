import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

def project(R, p):
    return [p(t) for t in R]

def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k,v) in R if k == key])) for key in keys]

class modeLocationCount(dml.Algorithm):
    contributor = 'jkmoy_mfflynn'
    reads = ['jkmoy_mfflynn.accident', 'jkmoy_mfflynn.fatal_accident']
    writes = ['jkmoy_mfflynn.modeLocationCount']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')

        # transformation here
        collection = list(repo['jkmoy_mfflynn.accident'].find())
        collection2 = list(repo['jkmoy_mfflynn.fatal_accident'].find())

        # non-fatal
        data = [((doc['mode_type'], doc['location_type']), 1) for doc in collection]
        data = aggregate(data, sum)
        while (len(data) > 6):
            for x in data:
                if x[0][1] == "Other":
                    data.remove(x)
        totalBike = 0
        totalMv = 0
        totalP = 0
        for x in data:
            if x[0][0] == 'bike':
                totalBike += x[1]
            elif x[0][0] == 'ped':
                totalP += x[1]
            else:
                totalMv += x[1]
            
        # fatal
        data2 = [((doc['mode_type'], doc['location_type']), 1) for doc in collection2]
        data2 = aggregate(data2, sum)
        for x in data2:
            if x[0][0] == 'bike':
                totalBike += x[1]
            elif x[0][0] == 'ped':
                totalP += x[1]
            else:
                totalMv += x[1]

        combined = []
        for j in range(len(data)):
            for k in range(len(data2)):
                if (data[j][0] == data2[k][0]):
                    x = (data[j][0], data[j][1]+data2[k][1])
                    combined.append(x)

        final = []
        for x in combined:
            if x[0][0] ==  'bike':
                a = ((x[0][0], x[0][1]), x[1], x[1]/totalBike)
                final.append(a)
            elif x[0][0] == 'mv':
                a = ((x[0][0], x[0][1]), x[1], x[1]/totalMv)
                final.append(a)
            else:
                a = ((x[0][0], x[0][1]), x[1], x[1]/totalP)
                final.append(a)

        final = project(final, lambda t: (t[0][0], t[0][1], t[1], t[2]))

        finalDataset = [{'Mode':tup[0] ,'Location_type':tup[1] ,'Count':tup[2] ,'Percentage of Total':tup[3]} for tup in final]
        
        repo.dropCollection('jkmoy_mfflynn.modeLocationCount')
        repo.createCollection('jkmoy_mfflynn.modeLocationCount')
        
        repo['jkmoy_mfflynn.modeLocationCount'].insert_many(finalDataset)
        repo['jkmoy_mfflynn.modeLocationCount'].metadata({'complete': True})

        print(repo['jkmoy_mfflynn.modeLocationCount'].metadata())
        
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
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/jkmoy_mfflynn') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/jkmoy_mfflynn') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:jkmoy_mfflynn#modeLocationCount', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:modeLocation', {'prov:label':'Modes and location of accident', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_mode = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_mode, this_script)
        doc.usage(get_mode, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'})

        mode = doc.entity('dat:jkmoy_mfflynn#modes', {prov.model.PROV_LABEL:'Modes and location %', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(mode, this_script)
        doc.wasGeneratedBy(mode, get_mode, endTime)
        doc.wasDerivedFrom(mode, resource, get_mode, get_mode, get_mode)

        repo.logout()
                  
        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
averagePerDepartment.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
#modeLocationCount.execute()

## eof

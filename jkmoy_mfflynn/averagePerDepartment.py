import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k,v) in R if k == key])) for key in keys]

class averagePerDepartment(dml.Algorithm):
    contributor = 'jkmoy_mfflynn'
    reads = ['jkmoy_mfflynn.fire', 'jkmoy_mfflynn.fire_departments']
    writes = ['jkmoy_mfflynn.averagePerDepartment']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')

        # transformation here
        collection = list(repo['jkmoy_mfflynn.fire'].find())
        collection2 = list(repo['jkmoy_mfflynn.fire_departments'].find())
        
        data = [{'Neighborhood':doc['Neighborhood'].strip()} for doc in collection if doc['Neighborhood'] != '']
        s = []
        for x in data:
            x = (x['Neighborhood'].upper(), 1)
            s.append(x)

        a = aggregate(s, sum) # List of tuples with neighborhoods and amount of incidents
        
        data = [{'Neighborhood':doc['attributes']["PD"].strip()} for doc in collection2 if doc['attributes']["PD"].strip() != '']
        s = []
        for x in data:
            x = (x['Neighborhood'], 1)
            s.append(x)

        b = aggregate(s, sum)
        
        while(len(b) > 11):
            for x in b:
                if x[0] == 'FENWAY/KENMORE':
                    b.remove(x)
                elif x[0] == 'CENTRAL':
                    b.remove(x)
                elif x[0] == 'SOUTH END':
                    b.remove(x)
                elif x[0] == 'BACK BAY/BEACON HILL':
                    b.remove(x)
                    
        b.append(('BOSTON', 4))

        final = []
        for j in range(11):
            for k in range(11):
                if (a[j][0][:3] == b[k][0][:3]):
                    final.append((a[j][0], a[j][1] // b[k][1]))

        finalDataset = [{'Neighborhood':tup[0], 'Count':tup[1]} for tup in final]
        
        repo.dropCollection('jkmoy_mfflynn.averagePerDepartment')
        repo.createCollection('jkmoy_mfflynn.averagePerDepartment')
        
        repo['jkmoy_mfflynn.averagePerDepartment'].insert_many(finalDataset)
        repo['jkmoy_mfflynn.averagePerDepartment'].metadata({'complete': True})

        print(repo['jkmoy_mfflynn.averagePerDepartment'].metadata())
        
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

        this_script = doc.agent('alg:jkmoy_mfflynn#averagePerDepartment', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:fires', {'prov:label':'Incidents per department', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_avg = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_avg, this_script)
        doc.usage(get_avg, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'})

        avg = doc.entity('dat:jkmoy_mfflynn#averages', {prov.model.PROV_LABEL:'Average per department', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(avg, this_script)
        doc.wasGeneratedBy(avg, get_avg, endTime)
        doc.wasDerivedFrom(avg, resource, get_avg, get_avg, get_avg)

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
#averagePerDepartment.execute()

## eof

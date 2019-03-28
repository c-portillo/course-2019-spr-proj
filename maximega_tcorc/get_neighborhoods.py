import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class get_neighborhoods(dml.Algorithm):
    contributor = 'maximega_tcorc'
    reads = []
    writes = ['maximega_tcorc.neighborhoods']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        repo_name = get_neighborhoods.writes[0]
        # ----------------- Set up the database connection -----------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('maximega_tcorc', 'maximega_tcorc')

        
        #------------------ Data retrieval ---------------------
        url = 'https://data.cityofnewyork.us/resource/q2z5-ai38.json'
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        content = response.read()
        json_response = json.loads(content)
        json_string = json.dumps(json_response, sort_keys=True, indent=2)

        #----------------- Data insertion into Mongodb ------------------
        repo.dropCollection('neighborhoods')
        repo.createCollection('neighborhoods')
        repo[repo_name].insert_many(json_response)
        repo[repo_name].metadata({'complete':True})
        print(repo[repo_name].metadata())
        
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
        repo.authenticate('maximega_tcorc', 'maximega_tcorc')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        #resources:
        doc.add_namespace('nyu', 'https://data.cityofnewyork.us/resource/')
        #agent
        this_script = doc.agent('alg:maximega_tcorc#get_neighborhoods', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('nyu:q2z5-ai38.json', {'prov:label':'NYC Neighborhoods', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        
        get_neighborhoods = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_neighborhoods, this_script)
        doc.usage(get_neighborhoods, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )
    
        neighborhoods = doc.entity('dat:maximega_tcorc#neighborhoods', {prov.model.PROV_LABEL:'NYC Neighborhood Information', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_neighborhoods, endTime)
        doc.wasDerivedFrom(neighborhoods, resource, get_neighborhoods, get_neighborhoods, get_neighborhoods)

        repo.logout()
                
        return doc

 
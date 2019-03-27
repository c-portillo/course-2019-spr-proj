import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class get_census_income(dml.Algorithm):
    contributor = 'maximega_tcorc'
    reads = []
    writes = ['maximega_tcorc.census_income']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        repo_name = get_census_income.writes[0]
        # ----------------- Set up the database connection -----------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('maximega_tcorc', 'maximega_tcorc')
        
        # ------------------ Data retrieval ---------------------
        url = 'https://api.datausa.io/api/?sort=desc&show=geo&required=income&sumlevel=tract&year=2016&where=geo%3A16000US3651000'
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(request)
        content = response.read()

        json_response = json.loads(content)
        json_string = json.dumps(json_response, sort_keys=True, indent=2)
        
        insert_many_arr = []
        for arr in json_response['data']:
            insert_many_arr.append({
                'year': arr[0],
                'tract': arr[1],
                'income': arr[2]
            })

        # ----------------- Data insertion into Mongodb ------------------
        repo.dropCollection('census_income')
        repo.createCollection('census_income')
        repo[repo_name].insert_many(insert_many_arr)
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
        doc.add_namespace('dusa', 'https://api.datausa.io/')
        #agent
        this_script = doc.agent('alg:maximega_tcorc#get_census_income', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dusa:api', {'prov:label':'Census Tract AVG Income', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        
        get_census_income = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_census_income, this_script)
        doc.usage(get_census_income, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query': '?sort=desc&show=geo&required=income&sumlevel=tract&year=2016&where=geo%3A16000US3651000'
                  }
                  )
    
        census_income = doc.entity('dat:maximega_tcorc#census_income', {prov.model.PROV_LABEL:'NYC AVG Income per Census Tract', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(census_income, this_script)
        doc.wasGeneratedBy(census_income, get_census_income, endTime)
        doc.wasDerivedFrom(census_income, resource, get_census_income, get_census_income, get_census_income)

        repo.logout()
          
        return doc




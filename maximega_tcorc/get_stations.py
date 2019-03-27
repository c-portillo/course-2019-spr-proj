import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class get_stations(dml.Algorithm):
    contributor = 'maximega_tcorc'
    reads = []
    writes = ['maximega_tcorc.stations']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        repo_name = get_stations.writes[0]
        # ----------------- Set up the database connection -----------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('maximega_tcorc', 'maximega_tcorc')

        # ------------------ Data retrieval ---------------------
        url = 'http://datamechanics.io/data/maximega_tcorc/NYC_subway_exit_entrance.csv'
        data = pd.read_csv(url).to_json(orient = "records")
        json_response = json.loads(data)


        # ----------------- Data insertion into Mongodb ------------------
        repo.dropCollection('stations')
        repo.createCollection('stations')
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
        doc.add_namespace('dmc', 'http://datamechanics.io/data/maximega_tcorc/')
        #agent
        this_script = doc.agent('alg:maximega_tcorc#get_subway_stations', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dmc:NYC_subway_exit_entrance.csv', {'prov:label':'NYC Census Tract Information', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        
        get_subway_stations = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_subway_stations, this_script)
        doc.usage(get_subway_stations, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )
    
        subway_stations = doc.entity('dat:maximega_tcorc#stations', {prov.model.PROV_LABEL:'NYC Census Tract Information', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(subway_stations, this_script)
        doc.wasGeneratedBy(subway_stations, get_subway_stations, endTime)
        doc.wasDerivedFrom(subway_stations, resource, get_subway_stations, get_subway_stations, get_subway_stations)

        repo.logout()
                
        return doc


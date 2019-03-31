import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class registered_vs_historical_votes(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ["carlosp_jpva_tkay_yllescas.historical_votes"]
    writes = ['carlosp_jpva_tkay_yllescas.registered_vs_historical_votes']

    @staticmethod
    def execute(trial=False):
        print("registered_vs_historical_votes")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        
        historical = 'data/historical_votes.json'
        with open(historical, "r", encoding="utf8") as datafile:
            json_string = datafile.read()
        r = json.loads(json_string)
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("registered_vs_historical_votes")
        repo.createCollection("registered_vs_historical_votes")
            
        total_votes = {}
        for i in range(len(r)):
            # x is an election result by ward
            x = r[i]
            keys = x.keys()
            for k in keys:
                if k == "Election-Place":
                    year = x[k][0:4]
                else:
                    if year not in total_votes: 
                        total_votes[year] = {}
                    if not x[k][0].isdigit():
                        if x[k] not in total_votes[year]:
                            total_votes[year][x[k]] = int(x[k.strip("Candidate")]) 
                        else: 
                            total_votes[year][x[k]] += int(x[k.strip("Candidate")]) 
    
        repo['carlosp_jpva_tkay_yllescas.registered_vs_historical_votes'].insert_one(total_votes)
        repo['carlosp_jpva_tkay_yllescas.registered_vs_historical_votes'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.registered_vs_historical_votes'].metadata())

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
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#registered_vs_historical_votes',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_registeredvshistoricalVotes = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_registeredvshistoricalVotes, this_script)
        doc.usage(get_registeredvshistoricalVotes, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=registered_vs_historical_votes&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        registeredvshistoricalVotes = doc.entity('dat:carlosp_jpva_tkay_yllescas#registered_vs_historical_votes',
                                {prov.model.PROV_LABEL: 'Historical Votes', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(registeredvshistoricalVotes, this_script)
        doc.wasGeneratedBy(registeredvshistoricalVotes, get_registeredvshistoricalVotes, endTime)
        doc.wasDerivedFrom(registeredvshistoricalVotes, resource, get_registeredvshistoricalVotes, get_registeredvshistoricalVotes, get_registeredvshistoricalVotes)

        repo.logout()

        return doc

# registered_vs_historical_votes.execute()

## eof
# writes historical_votes to database
# has latinx voting data by ward for 1st and 2nd place, multiple years, city council race
# not using bc only has 1st and 2nd place votes

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class historical_votes_latinx(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = []
    writes = ['carlosp_jpva_tkay_yllescas.historical_votes_latinx']

    @staticmethod
    def execute(trial=False):
        print("historical_votes_latinx")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        file = 'data/historical_votes.json'
        with open(file, "r", encoding="utf8") as datafile:
            json_string = datafile.read()
        r = json.loads(json_string)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("historical_votes_latinx")
        repo.createCollection("historical_votes_latinx")
        repo['carlosp_jpva_tkay_yllescas.historical_votes_latinx'].insert_many(r)
        repo['carlosp_jpva_tkay_yllescas.historical_votes_latinx'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.historical_votes_latinx'].metadata())

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

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#historical_votes_latinx',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_historicalVotes = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_historicalVotes, this_script)
        doc.usage(get_historicalVotes, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=historical_votes_latinx&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        historicalVotes = doc.entity('dat:carlosp_jpva_tkay_yllescas#historical_votes_latinx',
                                {prov.model.PROV_LABEL: 'Historical Votes', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(historicalVotes, this_script)
        doc.wasGeneratedBy(historicalVotes, get_historicalVotes, endTime)
        doc.wasDerivedFrom(historicalVotes, resource, get_historicalVotes, get_historicalVotes, get_historicalVotes)

        repo.logout()

        return doc

# historical_votes_latinx.execute()

## eof
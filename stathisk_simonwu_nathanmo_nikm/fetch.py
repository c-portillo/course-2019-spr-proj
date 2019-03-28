import prov.model
import dml
import datetime
import pandas as pd
import json
import uuid

class fetch(dml.Algorithm):
    contributor = 'stathisk_simonwu_nathanmo_nikm'
    reads = []
    writes = ['stathisk_simonwu_nathanmo_nikm.democratic_primary', 'stathisk_simonwu_nathanmo_nikm.republican_primary', 'stathisk_simonwu_nathanmo_nikm.greenrainbow_primary', 'stathisk_simonwu_nathanmo_nikm.mapping']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')

        base_url = "http://electionstats.state.ma.us"
        democratic_primary_url = ("democratic_primary", "/elections/download/126693/precincts_include:1/")
        republican_primary_url = ("republican_primary", "/elections/download/126695/precincts_include:1/")
        greenrainbow_primary_url = ("greenrainbow_primary", "/elections/download/126694/precincts_include:1/")

        index_list = [democratic_primary_url, republican_primary_url, greenrainbow_primary_url]
        tag_url_list = [(x[0], base_url + x[1]) for x in index_list]

        # election data
        for tag, url in tag_url_list:
            df = pd.read_csv(url)
            df = df[1:]
            if trial:
                df = df[:10]

            # replace all columns that have .
            newname = {}
            for name in df.columns:
                if '.' in name:
                    newname[name] = name.replace('.', '')
            df.rename(columns=newname, inplace=True)

            json_mat = df.to_json(orient='records')
            repo.dropCollection(tag)
            repo.createCollection(tag)
            repo['stathisk_simonwu_nathanmo_nikm.' + tag].insert_many(json.loads(json_mat))
            repo['stathisk_simonwu_nathanmo_nikm.' + tag].metadata({'complete': True})


        # mapping relation
        df = pd.read_csv("http://datamechanics.io/data/uscitiesv1.4.csv")
        df = df[df["state_id"] == "MA"]
        json_mat = df.to_json(orient='records')
        repo.dropCollection('mapping')
        repo.createCollection('mapping')
        repo['stathisk_simonwu_nathanmo_nikm.mapping'].insert_many(json.loads(json_mat))
        repo['stathisk_simonwu_nathanmo_nikm.mapping'].metadata({'complete': True})

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}


    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        ''
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('ballot', 'http://electionstats.state.ma.us/')
        doc.add_namespace('mapping', 'https://simplemaps.com/data/us-cities/')

        this_script = doc.agent('alg:stathisk_simonwu_nathanmo_nikm#fetch',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:election',
                              {'prov:label': 'primary election data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_democratic = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_republican = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_greenrainbow = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_mapping = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_democratic, this_script)
        doc.wasAssociatedWith(get_republican, this_script)
        doc.wasAssociatedWith(get_greenrainbow, this_script)
        doc.wasAssociatedWith(get_mapping, this_script)

        doc.usage(get_democratic, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_republican, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_greenrainbow, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_mapping, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        democratic = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#democratic_primary',
                          {prov.model.PROV_LABEL: 'democratic election', prov.model.PROV_TYPE: 'ont:DataSet'})
        republican = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#republican_primary',
                                {prov.model.PROV_LABEL: 'republican election', prov.model.PROV_TYPE: 'ont:DataSet'})
        greenrainbow = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#greenrainbow_primary',
                                {prov.model.PROV_LABEL: 'greenrainbow election', prov.model.PROV_TYPE: 'ont:DataSet'})
        mapping = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#mapping',
                                  {prov.model.PROV_LABEL: 'county city mapping', prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(democratic, this_script)
        doc.wasAttributedTo(republican, this_script)
        doc.wasAttributedTo(greenrainbow, this_script)
        doc.wasAttributedTo(mapping, this_script)

        doc.wasGeneratedBy(democratic, get_democratic, endTime)
        doc.wasGeneratedBy(republican, get_republican, endTime)
        doc.wasGeneratedBy(greenrainbow, get_greenrainbow, endTime)
        doc.wasGeneratedBy(mapping, get_mapping, endTime)

        doc.wasDerivedFrom(democratic, resource, get_democratic, get_democratic, get_democratic)
        doc.wasDerivedFrom(republican, resource, get_republican, get_republican, get_republican)
        doc.wasDerivedFrom(greenrainbow, resource, get_greenrainbow, get_greenrainbow, get_greenrainbow)
        doc.wasDerivedFrom(mapping, resource, get_mapping, get_mapping, get_mapping)

        repo.logout()
        return doc



if __name__ == '__main__':
    fetch.execute(False)
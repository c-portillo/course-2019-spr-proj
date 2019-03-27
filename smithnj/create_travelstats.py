import json
import dml
import prov.model
import uuid
import pandas as pd
import datetime
import geopandas

############################################
# create_travelstats.py
# Script for transforming CTA Station Satistics
############################################

class create_travelstats(dml.Algorithm):
    contributor = 'smithnj'
    reads = []
    writes = ['smithnj.travelstats']

    @staticmethod
    def execute(trial=False):

        startTime = datetime.datetime.now()

        # ---[ Connect to Database ]---------------------------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        repo_name = 'smithnj.travelstats'
        # ---[ Grab Data ]-------------------------------------------
        df = pd.read_csv('http://datamechanics.io/data/smithnj/smithnj/CTA_Ridership_Totals.csv')
        # ---[ Begin Transformation ]--------------------------------
        df['date'] = pd.to_datetime(df['date'])  # Convert "date" index to datetime
        df.index = df['date']  # set dataframe index to date
        monthly_sums = df.groupby([df.index.month, df['station_id'], df['stationname']]).sum()  # find total num of travelers per station per month
        monthly_sums['rides'] = monthly_sums['rides'].apply(lambda x: x / 4)  # divide rides by four as data is over a four year period
        # ---[ Write Data to JSON ]----------------------------------
        monthly_sums = monthly_sums.reset_index()
        df_json = monthly_sums.to_json(orient='records')
        loaded = json.loads(df_json)
        # ---[ MongoDB Insertion ]-------------------------------------------
        repo.dropCollection('travelstats')
        repo.createCollection('travelstats')
        print('done')
        repo[repo_name].insert_many(loaded)
        repo[repo_name].metadata({'complete': True})
        # ---[ Finishing Up ]-------------------------------------------
        print(repo[repo_name].metadata())
        repo.logout()
        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:smithnj#travelstats',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        stationstats = doc.entity('dat:smithnj#stationstats', {'prov:label': 'Chicago L-Station Statistics', prov.model.PROV_TYPE:'ont:DataSet'})
        merge = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(merge, this_script)
        doc.usage(merge, stationstats, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        updated_with_stats = doc.entity('dat:smithnj#travelstats', {
            prov.model.PROV_LABEL: 'Chicago L-Station Statistics, including 4yr avg of ridership per per month per station',
            prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(updated_with_stats, this_script)
        doc.wasGeneratedBy(updated_with_stats, merge, endTime)
        doc.wasDerivedFrom(updated_with_stats, stationstats)

        repo.logout()

        return doc

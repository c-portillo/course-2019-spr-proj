import dml
import prov.model
import datetime
import uuid


class combineDemographics(dml.Algorithm):
    contributor = 'tlux'
    reads = ['tlux.Raw_Age_Demo', 'tlux.Raw_Race_Demo']
    writes = ['tlux.Age_Race']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets '''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tlux', 'tlux')

        age_demo_data = list(repo['tlux.Raw_Age_Demo'].find())
        filtered_age_data = []
        agg_age_data = {}
        keys = set()
        # selects values from 2010, also finds the keys
        for val in age_demo_data:
            if val['Decade'] == '2010':
                filtered_age_data.append(val)
            keys.add(val['Neighborhood'])
        for key in keys:
            agg_age_data[key] = []
            for val in filtered_age_data:
                if val['Neighborhood'] == key:
                    t = {val['Age Range']:
                        (val['Number of People'], val['Percent of Population'])}
                    agg_age_data[key].append(t)

        # removes extra space at end so that it matches the key in the other dataset
        agg_age_data['Mission Hill'] = agg_age_data.pop('Mission Hill ')

        race_demo_data = list(repo['tlux.Raw_Race_Demo'].find())
        filtered_race_data = []
        agg_race_data = {}
        keys = set()
        # selects values from 2010, also finds the keys
        for val in race_demo_data:
            if val['Decade'] == '2010':
                filtered_race_data.append(val)
            keys.add(val['Neighborhood'])
        # aggregates values under the same neighborhood
        for key in keys:
            agg_race_data[key] = []
            for val in filtered_race_data:
                if val['Neighborhood'] == key:
                    t = {val['Race and or Ethnicity']:
                        (val['Number of People'], val['Percent of Population'])}
                    agg_race_data[key].append(t)

        # combines the two data sets
        final = []
        for key in agg_race_data.keys():
            final.append({'_id':key, 'Age Demographics': agg_age_data[key],
                          'Race Demographics': agg_race_data[key]})

        repo.dropCollection("Age_Race")
        repo.createCollection("Age_Race")
        repo['tlux.Age_Race'].insert_many(final)
        repo['tlux.Age_Race'].metadata({'complete': True})
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
        repo.authenticate('tlux', 'tlux')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:tlux#percentOpenSpace',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        race_demo_input = doc.entity('dat:tlux#Raw_Race_Demo',
                                     {prov.model.PROV_LABEL: 'Race Demographics',
                                      prov.model.PROV_TYPE: 'ont:DataSet'})
        age_demo_input = doc.entity('dat:tlux#Raw_Age_Demo',
                              {prov.model.PROV_LABEL: 'Age Demographics',
                               prov.model.PROV_TYPE: 'ont:DataSet'})

        combine_demo = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.usage(combine_demo, race_demo_input, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'}
                  )
        doc.usage(combine_demo, age_demo_input, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'}
                  )

        age_race = doc.entity('dat:tlux#Age_Race',
                                {prov.model.PROV_LABEL: 'Percent of Open Spaces by District',
                                 prov.model.PROV_TYPE: 'ont:DataSet'}
                                )

        doc.wasAssociatedWith(combine_demo, this_script)
        doc.wasAttributedTo(age_race, this_script)
        doc.wasGeneratedBy(age_race, combine_demo, endTime)
        doc.wasDerivedFrom(age_race, race_demo_input, combine_demo,
                           combine_demo, combine_demo)
        doc.wasDerivedFrom(age_race, age_demo_input, combine_demo,
                           combine_demo, combine_demo)
        return doc

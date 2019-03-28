import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class non_poc_early_voting(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ['carlosp_jpva_tkay_yllescas.early_voting', 'carlosp_jpva_tkay_yllescas.demographics_by_towns']
    writes = ['carlosp_jpva_tkay_yllescas.non_poc_early_voting']

    @staticmethod
    def execute(trial=False):
        print("non_poc_early_voting")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        repo.dropCollection("non_poc_early_voting")
        repo.createCollection("non_poc_early_voting")

        early_voting = (repo['carlosp_jpva_tkay_yllescas.early_voting']).find()
        town_dem = repo['carlosp_jpva_tkay_yllescas.demographics_by_towns']
        non_poc_early_voting = {}
        for voting in early_voting:
            for demo in town_dem.find():
                if (voting["City/Town"] != "Grand Total") and (demo["Community"].upper() in voting["City/Town"]) :
                    voting["White"] = float(demo["White"].replace(',',''))/float(demo["Population 2010"].replace(',', ''))
            if (voting["City/Town"] != "Grand Total"):
                non_poc_early_voting[voting["City/Town"]] = (voting["Percentage of Early Voters"], voting["White"])

        final_data = [{x:{"Percentage of Early Voters": non_poc_early_voting[x][0], "Non-POC Voters": round((non_poc_early_voting[x][1]*100), 2)}} for x in non_poc_early_voting]
        repo['carlosp_jpva_tkay_yllescas.non_poc_early_voting'].insert_many(final_data)
        repo['carlosp_jpva_tkay_yllescas.non_poc_early_voting'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.non_poc_early_voting'].metadata())

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
        doc.add_namespace('alg', './carlosp_jpva_tkay_yllescas')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', './data')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('dat_online', 'http://datamechanics.io/data/carlosp_jpva_tkay_yllescas')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#non_poc_early_voting',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        voting_data = doc.entity('dat:data#mass_early_voting',
                              {'prov:label': 'Early Voting in Mass per Town', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        demographics_data = doc.entity('dat_online:data#demographics_by_towns',
                              {'prov:label': 'Massachusetts Demographics by Town', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_nonPocEarlyVoting = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nonPocEarlyVoting, this_script)

        doc.usage(get_nonPocEarlyVoting, voting_data, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(get_nonPocEarlyVoting, demographics_data, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        non_poc_early_voting = doc.entity('dat:/non_poc_early_voting', {prov.model.PROV_LABEL:'Amount of early voters which are not poc per town', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(non_poc_early_voting, this_script)
        doc.wasGeneratedBy(non_poc_early_voting, get_nonPocEarlyVoting, endTime)
        doc.wasDerivedFrom(non_poc_early_voting, voting_data, get_nonPocEarlyVoting, get_nonPocEarlyVoting, get_nonPocEarlyVoting)
        doc.wasDerivedFrom(non_poc_early_voting, demographics_data, get_nonPocEarlyVoting, get_nonPocEarlyVoting, get_nonPocEarlyVoting)

        repo.logout()

        return doc

<<<<<<< HEAD
=======
#non_poc_early_voting.execute()
'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
>>>>>>> transformation3

## eof
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class city_race_diff_to_flip(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ["carlosp_jpva_tkay_yllescas.results_2017"]
    writes = ['carlosp_jpva_tkay_yllescas.city_race_diff_to_flip']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        repo.dropCollection("city_race_diff_to_flip")
        repo.createCollection("city_race_diff_to_flip")

        city_council_race = (repo['carlosp_jpva_tkay_yllescas.results_2017']).find()
        winner = {"Candidate":"", "Total":0}
        runner_up = {"Candidate":"", "Total":0}
        for nominee in city_council_race:
            if int(nominee["Total"].replace(",", "")) > winner["Total"]:
                winner = {x:int(nominee[x].replace(",", "")) for x in nominee if (x != "_id" and x != "Candidate")}
                winner["Candidate"] = nominee["Candidate"]
            elif int(nominee["Total"].replace(",", "")) > runner_up["Total"]:
                runner_up = {x:int(nominee[x].replace(",", "")) for x in nominee if (x != "_id" and x != "Candidate")}
                runner_up["Candidate"] = nominee["Candidate"]


        winner_and_runner_up = {"winner":winner, "runner_up":runner_up, "diff_by_ward":{},
                                "total_diff":abs((winner["Total"] - runner_up["Total"]))}
        for wards in winner:
            if wards != "Candidate":
                diff = abs(winner[wards] - winner[wards])
                winner_and_runner_up["diff_by_ward"][wards] = diff

        repo['carlosp_jpva_tkay_yllescas.city_race_diff_to_flip'].insert_one(winner_and_runner_up)
        repo['carlosp_jpva_tkay_yllescas.city_race_diff_to_flip'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.city_race_diff_to_flip'].metadata())

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
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#city_race_diff_to_flip',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        city_council_race_data = doc.entity('dat:data#results_2017',
                                            {'prov:label': 'Boston City Council race results for 2017 for each ward',
                                             prov.model.PROV_TYPE: 'ont:DataResource',
                                             'ont:Extension': 'json'})

        get_race_winners = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_race_winners, this_script)

        doc.usage(get_race_winners, city_council_race_data, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'})


        city_race_diff_to_flip = doc.entity('dat:/city_race_diff_to_flip',
                                            {prov.model.PROV_LABEL: '',
                                             prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(city_race_diff_to_flip, this_script)
        doc.wasGeneratedBy(city_race_diff_to_flip, get_race_winners, endTime)
        doc.wasDerivedFrom(city_race_diff_to_flip, city_council_race_data, get_race_winners,
                           get_race_winners, get_race_winners)

        repo.logout()

        return doc

#city_race_diff_to_flip.execute()


## eof

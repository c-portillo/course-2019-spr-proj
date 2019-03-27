import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class town(dml.Algorithm):
    contributor = 'robinhe_rqtian_hongyf_zhjiang'
    reads = []
    writes = ['town']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('robinhe_rqtian_hongyf_zhjiang', 'robinhe_rqtian_hongyf_zhjiang')

        # Read resource data.
        url = 'http://datamechanics.io/data/robinhe_rqtian_hongyf_zhjiang/data_diff_town.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        json_r = json.loads(response)

        # Project resource to output, in order to eliminate useless attributes
        outputs = []
        for item in json_r:
            output = {}
            if "Crash Number" in item.keys():
                output['Crash Number'] = item['Crash Number']
            elif "RMV Crash Number" in item.keys():
                output['Crash Number'] = item['RMV Crash Number']
            else:
                continue
            output["Crash Date"] = item["Crash Date"]
            output["Crash Time"] = item["Crash Time"]
            output["City/Town"] = item["City/Town"]
            outputs.append(output)
        repo.dropCollection("town")
        repo.createCollection("town")
        repo['robinhe_rqtian_hongyf_zhjiang.town'].insert_many(outputs)
        repo['robinhe_rqtian_hongyf_zhjiang.town'].metadata({'complete':True})
        print(repo['robinhe_rqtian_hongyf_zhjiang.town'].metadata())

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

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
        repo.authenticate('robinhe_rqtian_hongyf_zhjiang', 'robinhe_rqtian_hongyf_zhjiang')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        # Data resource
        doc.add_namespace('dsrc', 'http://datamechanics.io/data/robinhe_rqtian_hongyf_zhjiang/')

        this_script = doc.agent('alg:robinhe_rqtian_hongyf_zhjiang#town_projection',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dsrc:town_original',
                              {'prov:label': 'original town data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        project_town = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(project_town, this_script)
        doc.usage(project_town, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        town = doc.entity('dat:robinhe_rqtian_hongyf_zhjiang#town',
                          {prov.model.PROV_LABEL: 'crash data in different towns', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(town, this_script)
        doc.wasGeneratedBy(town, project_town, endTime)
        doc.wasDerivedFrom(town, resource, project_town, project_town, project_town)

        repo.logout()

        return doc

town.execute();
doc = town.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
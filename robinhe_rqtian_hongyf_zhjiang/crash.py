import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class crash(dml.Algorithm):
    contributor = 'robinhe_rqtian_hongyf_zhjiang'
    reads = []
    writes = ['crash']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('robinhe_rqtian_hongyf_zhjiang', 'robinhe_rqtian_hongyf_zhjiang')

        # Read resource data.
        url = 'http://datamechanics.io/data/robinhe_rqtian_hongyf_zhjiang/crash_data_01_19.json'
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
            output["Number of NonFatal Injuries"] = item["Number of NonFatal Injuries"];
            output["Number of Fatal Injuries"] = item["Number of Fatal Injuries"]
            output["Weather Condition"] = item["Weather Condition"]
            output["Ambient Light"] = item["Ambient Light"]
            outputs.append(output)
        repo.dropCollection("crash")
        repo.createCollection("crash")
        repo['robinhe_rqtian_hongyf_zhjiang.crash'].insert_many(outputs)
        repo['robinhe_rqtian_hongyf_zhjiang.crash'].metadata({'complete':True})
        print(repo['robinhe_rqtian_hongyf_zhjiang.crash'].metadata())

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

        this_script = doc.agent('alg:robinhe_rqtian_hongyf_zhjiang#crash_projection',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dsrc:crash_original',
                              {'prov:label': 'original carsh data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        project_crash = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(project_crash, this_script)
        doc.usage(project_crash, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        crash = doc.entity('dat:robinhe_rqtian_hongyf_zhjiang#crash',
                          {prov.model.PROV_LABEL: 'crash data from 01 to 19', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crash, this_script)
        doc.wasGeneratedBy(crash, project_crash, endTime)
        doc.wasDerivedFrom(crash, resource, project_crash, project_crash, project_crash)

        repo.logout()

        return doc

crash.execute();
doc = crash.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
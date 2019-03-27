import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class units(dml.Algorithm):
    contributor = 'robinhe_rqtian_hongyf_zhjiang'
    reads = []
    writes = ['units']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('robinhe_rqtian_hongyf_zhjiang', 'robinhe_rqtian_hongyf_zhjiang')

        # Read resource data.
        url = 'http://datamechanics.io/data/robinhe_rqtian_hongyf_zhjiang/revere_units_added.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        json_r = json.loads(response)

        # Project resource to output, in order to eliminate useless attributes
        outputs = []
        year_counts = {}
        for item in json_r:
            if item["Year"] in year_counts:
                year_counts[item["Year"]] += item["# of units"]
            else:
                year_counts[item["Year"]] = item["# of units"]
        for (k,v) in year_counts.items():
            output = {}
            output["Year"] = k;
            output["Number of units"] = v
            outputs.append(output)
        repo.dropCollection("units")
        repo.createCollection("units")
        repo['robinhe_rqtian_hongyf_zhjiang.units'].insert_many(outputs)
        repo['robinhe_rqtian_hongyf_zhjiang.units'].metadata({'complete':True})
        print(repo['robinhe_rqtian_hongyf_zhjiang.units'].metadata())

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

        this_script = doc.agent('alg:robinhe_rqtian_hongyf_zhjiang#units_aggregate',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dsrc:units_original',
                              {'prov:label': 'original units data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        project_crash = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(project_crash, this_script)
        doc.usage(project_crash, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        crash = doc.entity('dat:robinhe_rqtian_hongyf_zhjiang#units',
                          {prov.model.PROV_LABEL: 'units added per year', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crash, this_script)
        doc.wasGeneratedBy(crash, project_crash, endTime)
        doc.wasDerivedFrom(crash, resource, project_crash, project_crash, project_crash)

        repo.logout()

        return doc

units.execute();
doc = units.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
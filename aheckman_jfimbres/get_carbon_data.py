import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class get_carbon_data(dml.Algorithm):
    contributor = 'aheckman_jfimbres'
    reads = []
    writes = ['aheckman_jfimbres.co2_adjusted', 'aheckman_jfimbres.co2_unadjusted', 'aheckman_jfimbres.carbon_intesity']

    @staticmethod
    def execute(trial = False):
        '''Retrieve data sets on carbon emissions from datamechanics.io.'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')

        url = 'http://datamechanics.io/data/carbon_adjusted.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("co2_adjusted")
        repo.createCollection("co2_adjusted")
        repo['aheckman_jfimbres.co2_adjusted'].insert_many(r)

        url = 'http://datamechanics.io/data/carbon_unadjusted.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("co2_unadjusted")
        repo.createCollection("co2_unadjusted")
        repo['aheckman_jfimbres.co2_unadjusted'].insert_many(r)

        url = 'http://datamechanics.io/data/carbon_intensity.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("carbon_intensity")
        repo.createCollection("carbon_intensity")
        repo['aheckman_jfimbres.carbon_intensity'].insert_many(r)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''


        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:aheckman_jfimbres#get_carbon_data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_co2_adjusted = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_co2_unadjusted = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_carbon_intensity = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_co2_adjusted, this_script)
        doc.wasAssociatedWith(get_co2_unadjusted, this_script)
        doc.wasAssociatedWith(get_carbon_intensity, this_script)
        doc.usage(get_co2_adjusted, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Absolute&$select=Absolute,Percent,State,2016,2015,2014,2013,2012,2011,2010,2008,2008,2007,2006,2005,'
                  }
                  )
        doc.usage(get_co2_unadjusted, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Total&$select=Total,Transportation,Industrial,Residential,Electric+Power,Commercial,State'
                   }
                  )
        doc.usage(get_carbon_intensity, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Absolute&$select=Absolute,Percent,State,2016,2015,2014,2013,2012,2011,2010,2008,2008,2007,2006,2005,'
                   }
                  )

        co2_adjusted = doc.entity('dat:aheckman_jfimbres#co2_adjusted', {prov.model.PROV_LABEL:'Adjusted Carbon Emissions', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(co2_adjusted, this_script)
        doc.wasGeneratedBy(co2_adjusted, get_co2_adjusted, endTime)
        doc.wasDerivedFrom(co2_adjusted, resource, get_co2_adjusted, get_co2_adjusted, get_co2_adjusted)

        co2_unadjusted = doc.entity('dat:aheckman_jfimbres#co2_unadjusted', {prov.model.PROV_LABEL:'Unadjusted Carbon Emissions', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(co2_unadjusted, this_script)
        doc.wasGeneratedBy(co2_unadjusted, get_co2_unadjusted, endTime)
        doc.wasDerivedFrom(co2_unadjusted, resource, get_co2_unadjusted, get_co2_unadjusted, get_co2_unadjusted)

        carbon_intensity = doc.entity('dat:aheckman_jfimbres#carbon_intensity', {prov.model.PROV_LABEL:'Carbon Intensity', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(carbon_intensity, this_script)
        doc.wasGeneratedBy(carbon_intensity, get_carbon_intensity, endTime)
        doc.wasDerivedFrom(carbon_intensity, resource, get_carbon_intensity)

        return doc

get_carbon_data.execute()
## eof
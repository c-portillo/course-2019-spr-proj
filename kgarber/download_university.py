import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

# This algorithm downloads the university geojson dataset and stores it in mongodb

class download_university(dml.Algorithm):
    contributor = 'kgarber'
    reads = []
    writes = ['kgarber.university']

    @staticmethod
    def execute(trial = False):
        print("Starting download_university algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')

        # download the data and insert it into MongoDB
        # https://data.boston.gov/dataset/colleges-and-universities
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/cbf14bb032ef4bd38e20429f71acb61a_2.geojson'
        print("Downloading university dataset.")
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        print("Saving dataset to MongoDB.")
        repo.dropCollection("university")
        repo.createCollection("university")
        repo['kgarber.university'].insert_many(r["features"])
        repo['kgarber.university'].metadata({'complete':True})

        # close the database connection and end the algorithm
        repo.logout()
        endTime = datetime.datetime.now()
        print("Done with download_university algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        # the namespace for geospatial datasets in boston data portal
        doc.add_namespace('bgd', 'http://bostonopendata-boston.opendata.arcgis.com/datasets')

        # the agent which is my algorithn
        this_script = doc.agent(
            'alg:kgarber#download_university', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })
        # the entity I am downloading
        resource = doc.entity(
            'bgd:universities',
            {
                'prov:label':'University Dataset', 
                prov.model.PROV_TYPE:'ont:DataResource', 
                'ont:Extension':'geojson'
            })
        # the activity of downloading this dataset (log the timing)
        get_university = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        # the activity is associated with the agent
        doc.wasAssociatedWith(get_university, this_script)
        # log an invocation of the activity
        doc.usage(get_university, resource, startTime, None,
            {
                prov.model.PROV_TYPE:'ont:Retrieval',
                'ont:Query':'/cbf14bb032ef4bd38e20429f71acb61a_2.geojson'
            })
        # the newly generated entity
        university = doc.entity(
            'dat:kgarber#university', 
            {
                prov.model.PROV_LABEL:'Universities In Boston', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        # relations for the above entity
        doc.wasAttributedTo(university, this_script)
        doc.wasGeneratedBy(university, get_university, endTime)
        doc.wasDerivedFrom(university, resource, get_university, get_university, get_university)
        
        # return the generated provenance document
        return doc


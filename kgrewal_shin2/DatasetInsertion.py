
import urllib.request
import requests
import json
import dml
import prov.model
import datetime
import uuid


class DatasetInsertion(dml.Algorithm):
    contributor = 'kgrewal_shin2'
    reads = []
    writes = ['kgrewal_shin2.street_names', 'kgrewal_shin2.landmarks', 'kgrewal_shin2.neighborhoods',
              'kgrewal_shin2.ubers', 'kgrewal_shin2.pub_schools']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgrewal_shin2', 'kgrewal_shin2')

        # boston street names
        url = 'http://datamechanics.io/data/boston_street_names.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        repo.dropCollection("street_names")
        repo.createCollection("street_names")
        repo['kgrewal_shin2.street_names'].insert_many(r)
        repo['kgrewal_shin2.street_names'].metadata({'complete': True})
        print(repo['kgrewal_shin2.street_names'].metadata())


        #landmarks api
        url = 'https://opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.geojson'
        response = requests.get(url)
        responsetxt = '[' + response.text + ']'
        r = json.loads(responsetxt)
        repo.dropCollection("landmarks")
        repo.createCollection("landmarks")
        repo['kgrewal_shin2.landmarks'].insert_many(r)
        repo['kgrewal_shin2.landmarks'].metadata({'complete': True})
        print(repo['kgrewal_shin2.landmarks'].metadata())


        # neighborhoods
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/boston.geojson"
        response = requests.get(url)
        responsetxt = '[' + response.text + ']'
        r = json.loads(responsetxt)
        repo.dropCollection("neighborhoods")
        repo.createCollection("neighborhoods")
        repo['kgrewal_shin2.neighborhoods'].insert_many(r)
        repo['kgrewal_shin2.neighborhoods'].metadata({'complete': True})
        print(repo['kgrewal_shin2.neighborhoods'].metadata())

        # Public Schools
        url = "http://bostonopendata-boston.opendata.arcgis.com/datasets/1d9509a8b2fd485d9ad471ba2fdb1f90_0.geojson"
        response = requests.get(url)
        responsetxt = '[' + response.text + ']'
        r = json.loads(responsetxt)
        repo.dropCollection("pub_schools")
        repo.createCollection("pub_schools")
        repo['kgrewal_shin2.pub_schools'].insert_many(r)
        repo['kgrewal_shin2.pub_schools'].metadata({'complete': True})
        print(repo['kgrewal_shin2.pub_schools'].metadata())

        #uber data
        url = 'http://datamechanics.io/data/boston_common_ubers.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        repo.dropCollection("ubers")
        repo.createCollection("ubers")
        repo['kgrewal_shin2.ubers'].insert_many(r)
        repo['kgrewal_shin2.ubers'].metadata({'complete': True})
        print(repo['kgrewal_shin2.ubers'].metadata())

        # major roads
        # url = 'major_roads.json'
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        # r = json.loads(response)
        # with open('major_roads.json') as f:
        #     r = json.load(f)
        # repo.dropCollection("major_roads")
        # repo.createCollection("major_roads")
        # repo['kgrewal_shin2.major_roads'].insert_many(r)
        # repo['kgrewal_shin2.major_roads'].metadata({'complete': True})
        # print(repo['kgrewal_shin2.major_roads'].metadata())

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
        repo.authenticate('kgrewal_shin2', 'kgrewal_shin2')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:kgrewal_shin2#DatasetInsertion',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_street_name = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_landmarks = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_neighborhoods = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_ubers = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_pub_schools = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_street_name, this_script)
        doc.usage(get_street_name, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Street+Name&$select=full_name,gender,zipcodes,rank,street_name'
                   }
                  )

        doc.usage(get_landmarks, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Landmark+Name&$select=WARD, Petition, Name_of_Pr, Address, Neighborho, '
                              'ShapeSTArea, ShapeSTLength'
                  }
                  )

        doc.usage(get_neighborhoods, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Neighborhood+Location&$select=features'}
                  )

        doc.usage(get_ubers, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Uber+Data&$select=Origin Display Name,Destination Display Name,Mean Travel Time '
                              '(Seconds),Range - Lower Bound Travel Time (Seconds),Range - Upper Bound Travel Time (Seconds)'
                  }
                  )

        doc.usage(get_pub_schools, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Public+School&$select=X,Y,BLDG_NAME,ADDRESS'
                   }
                  )


        streets = doc.entity('dat:kgrewal_shin2#street_name',
                          {prov.model.PROV_LABEL: 'Boston Streets', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(streets, this_script)
        doc.wasGeneratedBy(streets, get_street_name, endTime)
        doc.wasDerivedFrom(streets, resource, get_street_name, get_street_name, get_street_name)

        landmarks = doc.entity('dat:kgrewal_shin2#landmarks',
                          {prov.model.PROV_LABEL: 'Boston Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(landmarks, this_script)
        doc.wasGeneratedBy(landmarks, get_landmarks, endTime)
        doc.wasDerivedFrom(landmarks, resource, get_landmarks, get_landmarks, get_landmarks)


        neighborhoods = doc.entity('dat:kgrewal_shin2#neighborhoods',
                          {prov.model.PROV_LABEL: 'Boston Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_neighborhoods, endTime)
        doc.wasDerivedFrom(neighborhoods, resource, get_neighborhoods, get_neighborhoods, get_neighborhoods)

        ubers = doc.entity('dat:kgrewal_shin2#ubers',
                          {prov.model.PROV_LABEL: 'Boston Common Ubers', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(ubers, this_script)
        doc.wasGeneratedBy(ubers, get_ubers, endTime)
        doc.wasDerivedFrom(ubers, resource, get_ubers, get_ubers, get_ubers)

        pub_schools = doc.entity('dat:kgrewal_shin2#pub_schools',
                           {prov.model.PROV_LABEL: 'Public Schools', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(pub_schools, this_script)
        doc.wasGeneratedBy(pub_schools, get_pub_schools, endTime)
        doc.wasDerivedFrom(pub_schools, resource, get_pub_schools, get_pub_schools, get_pub_schools)


        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
DatasetInsertion.execute()
doc = DatasetInsertion.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
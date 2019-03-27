
import json
import dml
import prov.model
import datetime
import uuid

class transformation1():

    contributor = 'kgrewal_shin2'
    reads = ['kgrewal_shin2.landmarks', 'kgrewal_shin2.street_names']
    writes = ['kgrewal_shin2.streets_without_landmarks']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgrewal_shin2', 'kgrewal_shin2')

        landmarks = repo.kgrewal_shin2.landmarks.find()
        street_names = repo.kgrewal_shin2.street_names.find()

        landmark_streets = []
        for l in landmarks:
            length = len(l['features'])
            for i in range(length):
                data = l['features'][i]['properties']
                address = data['Address']

                if "Bounded by" not in address:
                    street = address.split(" ", 1)
                    if street[0].isdigit() or len(street[0].split("-")) > 1:
                        street = street[1]
                    else:
                        street = address
                else:
                    street = address.split("Bounded by ")[1]

                landmark_streets.append(street)

        streets_without_landmarks = []
        for x in street_names:
            full_name = x['full_name']
            #to correct for a comma at the end of full_name
            full_name = full_name[:-1]
            gender = x['gender']
            zipcode = x['zipcodes']
            street_name = x['street_name']

            # find difference of streetnames and landmarks, while selecting only those that aren't female
            if (full_name not in landmark_streets) and (gender != "female"):
                streets_without_landmarks.append({"full_name": full_name, "gender": gender,
                                                  "zipcode": zipcode, "street_name": street_name})


        repo.dropCollection("streets_without_landmarks")
        repo.createCollection("streets_without_landmarks")
        repo['kgrewal_shin2.streets_without_landmarks'].insert_many(streets_without_landmarks)
        repo['kgrewal_shin2.streets_without_landmarks'].metadata({'complete': True})
        print(repo['kgrewal_shin2.streets_without_landmarks'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}



    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
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

        this_script = doc.agent('alg:kgrewal_shin2#transformation1',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_streets = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_streets, this_script)
        doc.usage(get_streets, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Streets+Without+Landmarks&$select=full_name,gender,zipcode,street_name'
                   }
                  )

        orig_streets = doc.entity('dat:kgrewal_shin2#streets',
                          {prov.model.PROV_LABEL: 'Streets', prov.model.PROV_TYPE: 'ont:DataSet'})
        landmarks = doc.entity('dat:kgrewal_shin2#landmarks',
                          {prov.model.PROV_LABEL: 'Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        streets = doc.entity('dat:kgrewal_shin2#streets_without_landmarks',
                          {prov.model.PROV_LABEL: 'Streets Without Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(streets, this_script)
        doc.wasGeneratedBy(streets, get_streets, endTime)
        doc.wasDerivedFrom(orig_streets, resource, get_streets, get_streets, get_streets)
        doc.wasDerivedFrom(landmarks, resource, get_streets, get_streets, get_streets)

        repo.logout()

        return doc


transformation1.execute()
doc = transformation1.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


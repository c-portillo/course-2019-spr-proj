
import json
import dml
import prov.model
import datetime
import uuid

class transformation2():

    contributor = 'kgrewal_shin2'
    reads = ['kgrewal_shin2.pub_schools', 'kgrewal_shin2.street_names']
    writes = ['kgrewal_shin2.streets_without_schools']


    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgrewal_shin2', 'kgrewal_shin2')

        schools = repo.kgrewal_shin2.pub_schools.find()
        street_names = repo.kgrewal_shin2.street_names.find()

        school_streets = []
        for s in schools:
            length = len(s['features'])
            for i in range(length):
                data = s['features'][i]['properties']
                address = data['ADDRESS']

                street = address.split(" ", 1)
                if street[0].isdigit():
                    street = street[1]
                else:
                    street = address

                school_streets.append(street)

        streets_without_schools = []
        for x in street_names:
            full_name = x['full_name']
            #to correct for a comma at the end of full_name
            full_name = full_name[:-1]
            gender = x['gender']
            zipcode = x['zipcodes']
            street_name = x['street_name']

            # find difference of streetnames and schools
            if full_name not in school_streets and gender != "female":
                streets_without_schools.append({"full_name": full_name, "gender": gender,
                                                  "zipcode": zipcode, "street_name": street_name})

        repo.dropCollection("streets_without_schools")
        repo.createCollection("streets_without_schools")
        repo['kgrewal_shin2.streets_without_schools'].insert_many(streets_without_schools)
        repo['kgrewal_shin2.streets_without_schools'].metadata({'complete': True})
        print(repo['kgrewal_shin2.streets_without_schools'].metadata())

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

        this_script = doc.agent('alg:kgrewal_shin2#transformation2',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_streets = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_streets, this_script)
        doc.usage(get_streets, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Streets+Without+Schools&$select=full_name,gender,zipcode,street_name'
                   }
                  )

        orig_streets = doc.entity('dat:kgrewal_shin2#streets',
                          {prov.model.PROV_LABEL: 'Streets', prov.model.PROV_TYPE: 'ont:DataSet'})
        schools = doc.entity('dat:kgrewal_shin2#schools',
                          {prov.model.PROV_LABEL: 'Schools', prov.model.PROV_TYPE: 'ont:DataSet'})
        streets = doc.entity('dat:kgrewal_shin2#streets_without_schools',
                          {prov.model.PROV_LABEL: 'Streets Without Schools', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(streets, this_script)
        doc.wasGeneratedBy(streets, get_streets, endTime)
        doc.wasDerivedFrom(orig_streets, resource, get_streets, get_streets, get_streets)
        doc.wasDerivedFrom(schools, resource, get_streets, get_streets, get_streets)

        repo.logout()

        return doc


transformation2.execute()
doc = transformation2.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


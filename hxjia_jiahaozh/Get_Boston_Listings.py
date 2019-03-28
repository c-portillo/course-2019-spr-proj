import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class Get_Boston_Listings(dml.Algorithm):
    contributor = 'hxjia_jiahaozh'
    reads = []
    writes = ['hxjia_jiahaozh.listings']

    @staticmethod
    def execute(trial=False):
        """
            Retrieve some data sets (not using the API here for the sake of simplicity).
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')

        url = 'http://datamechanics.io/data/hxjia_jiahaozh/Listings.csv'
        df_listings = pd.read_csv(url)
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(df_listings.to_json(orient='records'))
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("listings")
        repo.createCollection("listings")
        repo['hxjia_jiahaozh.listings'].insert_many(r)
        repo['hxjia_jiahaozh.listings'].metadata({'complete': True})
        print(repo['hxjia_jiahaozh.listings'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        """
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
        """

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/hxjia_jiahaozh/bostonlistings') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/hxjia_jiahaozh/Listings')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')
        # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/?prefix=hxjia_jiahaozh/')

        this_script = doc.agent('alg:hxjia_jiahaozh#Get_Boston_Listings',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:Listings',
                              {'prov:label': 'data set of boston airbnb listings information, Service Request ', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_listings = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_listings, this_script)
        doc.usage(get_listings, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=listings&$select=id,number_of_reviews,review_scores_rating,room_type,neighbourhood,price'
                   }
                  )

        listings = doc.entity('dat:hxjia_jiahaozh#listings',
                          {prov.model.PROV_LABEL: 'Boston Listings', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(listings, this_script)
        doc.wasGeneratedBy(listings, get_listings, endTime)
        doc.wasDerivedFrom(listings, resource, get_listings, get_listings, get_listings)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Get_Boston_Listings.execute()
# doc = bostonlistings.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


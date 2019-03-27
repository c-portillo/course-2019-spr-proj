import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class Get_Boston_Reviews(dml.Algorithm):
    contributor = 'hxjia_jiahaozh'
    reads = []
    writes = ['hxjia_jiahaozh.reviews']

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

        url = 'http://data.insideairbnb.com/united-states/ma/boston/2019-01-17/data/reviews.csv.gz'
        df_reviews = pd.read_csv(url)
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(df_reviews.to_json(orient='records'))
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("reviews")
        repo.createCollection("reviews")
        repo['hxjia_jiahaozh.reviews'].insert_many(r)
        repo['hxjia_jiahaozh.reviews'].metadata({'complete': True})
        print(repo['hxjia_jiahaozh.reviews'].metadata())

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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/hxjia_jiahaozh/bostonreviews') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/hxjia_jiahaozh/Reviews')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')
        # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://data.insideairbnb.com/united-states/ma/boston/2019-01-17/data/')

        this_script = doc.agent('alg:hxjia_jiahaozh#Get_Boston_Reviews',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:reviews',
                              {'prov:label': 'data set of boston airbnb reviews information, Service Request ', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_reviews = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_reviews, this_script)
        doc.usage(get_reviews, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=reviews&$select=listing_id,id,date,reviewer_id,reviewer_name,comments'
                   }
                  )

        reviews = doc.entity('dat:hxjia_jiahaozh#reviwews',
                          {prov.model.PROV_LABEL: 'Boston Reviews', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(reviews, this_script)
        doc.wasGeneratedBy(reviews, get_reviews, endTime)
        doc.wasDerivedFrom(reviews, resource, get_reviews, get_reviews, get_reviews)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Get_Boston_Reviews.execute()
# doc = bostonreviews.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


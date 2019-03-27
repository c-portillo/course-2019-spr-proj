import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class Price_and_Comments(dml.Algorithm):
    contributor = 'hxjia_jiahaozh'
    reads = ['hxjia_jiahaozh.reviews', 'hxjia_jiahaozh.listings']
    writes = ['hxjia_jiahaozh.Price_and_Comments']

    @staticmethod
    def execute(trial=False):

        def project(R, p):
            return [p(t) for t in R]

        def select(R, s):
            return [t for t in R if s(t)]

        def product(R, S):
            return [(t, u) for t in R for u in S]

        def aggregate(R, f):
            keys = {r[0] for r in R}
            return [(key, f([v for (k, v) in R if k == key])) for key in keys]

        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')

        collection_reviews = repo.hxjia_jiahaozh.reviews
        reviews = collection_reviews.find({})
        collection_listings = repo.hxjia_jiahaozh.listings
        listings = collection_listings.find({})

        reviews_data = []
        listings_data = []
        for data in listings:
            listings_data.append(data)
#        print(listings_data)

        listings_data = project(listings_data, lambda t: [t['id'], t['price'].replace("$", "").replace(",", ""), t['review_scores_rating']])

        for data in reviews:
            reviews_data.append(data)

        reviews_data = project(reviews_data, lambda t: [t['listing_id'], t['comments']])

        reviews_data = aggregate(reviews_data, lambda t: t)

        result = product(listings_data, reviews_data)

        result = select(result, lambda t: t[0][0] == t[1][0])

        result = project(result, lambda t: (t[0][0], t[0][1], t[1][1], t[0][2]))

        result = project(result, lambda t: {'listing_id': t[0], 'price': t[1], 'reviews': t[2], 'review_score': t[3]})



        # r = json.loads(new_bl.to_json(orient='records'))
#        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("Price_and_Comments")
        repo.createCollection("Price_and_Comments")
        repo['hxjia_jiahaozh.Price_and_Comments'].insert_many(result)
        repo['hxjia_jiahaozh.Price_and_Comments'].metadata({'complete': True})
        print(repo['hxjia_jiahaozh.Price_and_Comments'].metadata())

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
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/hxjia_jiahaozh/')

        this_script = doc.agent('alg:hxjia_jiahaozh#price_and_comments',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource1 = doc.entity('bdp:listings',
                              {'prov:label': 'listins, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        resource2 = doc.entity('bdp:reviews',
                              {'prov:label': 'reviews, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        transformation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transformation, this_script)
        doc.usage(transformation, resource1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Transformation',
                   'ont:Query': '?type=listing&$select=listing_id, price, review_score'
                   }
                  )
        doc.usage(transformation, resource2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Transformation',
                   'ont:Query': '?type=reviews&$select=listing_id, comments'
                   }
                  )

        priceandcomments = doc.entity('dat:hxjia_jiahaozh#price_and_comments',
                          {prov.model.PROV_LABEL: 'Price and Comments', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(priceandcomments, this_script)
        doc.wasGeneratedBy(priceandcomments, transformation, endTime)
        doc.wasDerivedFrom(priceandcomments, resource1, transformation, transformation, transformation)
        doc.wasDerivedFrom(priceandcomments, resource2, transformation, transformation, transformation)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Price_and_Comments.execute()
# doc = Boston_Landmarks.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof

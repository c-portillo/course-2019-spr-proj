import json
import dml
import prov.model
import datetime
import uuid
# import pandas as pd


class Prices_Landmarks_Listings(dml.Algorithm):

    contributor = 'hxjia_jiahaozh'
    reads = ['hxjia_jiahaozh.listings', 'hxjia_jiahaozh.Boston_Landmarks']
    writes = ['hxjia_jiahaozh.prices_landmarks_listings']

    @staticmethod
    def execute(trial = False):

        # relational helper function
        def project(R, p):
            return [p(t) for t in R]
        def product(R, S):
            return [(t,u) for t in R for u in S]
        def select(R, s):
            return [t for t in R if s(t)]
        def aggregate(R, f):
            keys = {r[0] for r in R}
            return [(key, f([v for (k, v) in R if k == key])) for key in keys]

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')

        new_collection_name = 'prices_landmarks_listings'
        repo.dropCollection('hxjia_jiahaozh.'+new_collection_name)
        repo.createCollection('hxjia_jiahaozh.'+new_collection_name)

        collection_landmarks = repo.hxjia_jiahaozh.Boston_Landmarks
        cursor_landmarks = collection_landmarks.find()
        collection_listings = repo.hxjia_jiahaozh.listings
        cursor_listings = collection_listings.find()

        # For each neighborhood, we need (neighborhood, count of landmarks in that neighborhood).
        single_landmark = []
        for i in cursor_landmarks:
            single_landmark.append((i['Neighborhood'], 1))
        temp = select(single_landmark, lambda k: k[0] and k[0] != ' ' and k[0] != 'Waterfront' and k[0] != 'Boston')
        landmark_result = aggregate(temp, sum)
        landmark_result.append(('Allston-Brighton', 9))
        landmark_result.remove(('Allston', 1))
        landmark_result.remove(('Brighton', 8))
        landmark_result.append(('Fenway/Kenmore', 14))
        landmark_result.remove(('Fenway, JP', 1))
        landmark_result.remove(('Fenway', 13))
        landmark_result.remove(('Theater', 9))
        landmark_result.remove(('Theater District', 1))
        landmark_result.append(('Theater District', 10))
        landmark_result.remove(('Beacon Hill/Back Bay', 1))
        landmark_result.remove(('Beacon Hill', 1))
        landmark_result.append(('Beacon Hill', 2))
        landmark_result.append(('Leather District', 2))
        landmark_result.remove(('South Cove', 2))
        # print(landmark_result)

        # For each neighborhood we need (neighborhood, count of listings in that neighborhood).
        count_listing = []
        for j in cursor_listings:
            count_listing.append((j['neighbourhood'],  1))
        # print(count_listing)
        count_temp = select(count_listing, lambda k: k[0])
        # print(temp)
        nei_count = aggregate(count_temp, sum)
        # print(nei_count)

        # For each neighborhood we need (neighborhood, mean price in that neighborhood).
        cursor_listings = collection_listings.find()
        price_listing = []
        for h in cursor_listings:
            price_listing.append((h['neighbourhood'], h['price']))
        # print(price_listing)
        price_temp = select(price_listing, lambda k: k[0])
        # print(price_temp)
        price_temp = project(price_temp, lambda k: (k[0], float(k[1].replace('$', '').replace(',', ''))))
        # print(price_temp)
        nei_price = aggregate(price_temp, sum)
        # print(nei_price)
        nei_meanprice = []
        for m in range(len(nei_price)):
            nei_meanprice.append((nei_price[m][0], nei_price[m][1] / nei_count[m][1]))
        #print(nei_meanprice)

        # For each neighborhood we need (neighborhood,count of listings in that neighborhood,
        # mean price in that neighborhood).
        count_meanprice = [(i, m, round(n,1)) for ((i, m), (j, n)) in product(nei_count, nei_meanprice) if i == j]
        # print(count_meanprice)

        # [neighborhood, # of landmarks, # of listings, mean_price]
        final_result = [(i, m, n, p) for ((i, m), (j, n, p)) in product(landmark_result, count_meanprice) if i == j]

        filterr = lambda t: {'Neighbourhood': t[0],
                            '# of Landmarks': t[1],
                            '# of Listings': t[2],
                            'Mean Price': t[3]}

        result_with_name = project(final_result, filterr)
        # print(result_with_name)

        repo['hxjia_jiahaozh.'+new_collection_name].insert_many(result_with_name)

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
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/Prices_Landmarks_Listings')
        doc.add_namespace('dat', 'http://datamechanics.io/data/hxjia_jiahaozh/prices_landmarks_listings')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        doc.add_namespace('bdp', 'http://datamechanics.io/?prefix=hxjia_jiahaozh/')

        this_script = doc.agent('alg:hxjia_jiahaozh#prices_landmarks_listings', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

        resource1 = doc.entity('bdp:Get_Boston_Listings', {'prov:label': 'data set of boston airbnb listings information, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource2 = doc.entity('bdp:get_boston_landmark', {'prov:label': 'data set of boston landmark information, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})

        transformation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transformation, this_script)

        doc.usage(transformation, resource1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': '?type=listing&$select=neighbourhood, price'})
        doc.usage(transformation, resource2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': '?type=landmark&$select=neighborhood'})

        price_landmarks_listings = doc.entity('dat:hxjia_jiahaozh#price_landmark_listings', {prov.model.PROV_LABEL: 'Price_landmarks_Listings', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(price_landmarks_listings, this_script)
        doc.wasGeneratedBy(price_landmarks_listings, transformation, endTime)
        doc.wasDerivedFrom(price_landmarks_listings, resource1, transformation, transformation, transformation)
        doc.wasDerivedFrom(price_landmarks_listings, resource2, transformation, transformation, transformation)

        repo.logout()
        return doc


#Prices_Landmarks_Listings.execute()
# doc = Prices_Landmarks_Listings.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
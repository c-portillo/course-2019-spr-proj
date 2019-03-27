import dml
import datetime
import json
import prov.model
import pprint
import uuid



class CvsWalgreen(dml.Algorithm):

    contributor = "jshen97_leochans"
    reads = ['jshen97_leochans.cvs', 'jshen97_leochans.walgreen']
    writes = ['jshen97_leochans.cvsWalgreen']

    @staticmethod
    def execute(trial=False):

        start_time = datetime.datetime.now()

        # set up database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('leochans_jshen97', 'leochans_jshen97')

        # create the result collections
        repo.dropCollection('cvsWalgreen')
        repo.createCollection('cvsWalgreen')

        # insert the geolocation, name, google place_id, rating, and rating_counts
        # name will be either cvs or walgreen
        for document in repo.jshen97_leochans.cvs.find():
            if 'results' in document.keys():
                for item in document['results']:
                    d = {
                        'name': 'CVS',
                        'location': item['geometry']['location'],
                        'place_id': item['place_id'],
                        'rating': item['rating'] if 'rating' in item.keys() else None,
                        'rating_count': item['user_ratings_total'] if 'user_ratings_total' in item.keys() else None
                    }
                    repo['jshen97_leochans.cvsWalgreen'].insert_one(d)
            else:
                continue

        for document in repo.jshen97_leochans.walgreen.find():
            if 'results' in document.keys():
                for item in document['results']:
                    d = {
                        'name': 'Walgreen',
                        'location': item['geometry']['location'],
                        'place_id': item['place_id'],
                        'rating': item['rating'] if 'rating' in item.keys() else None,
                        'rating_count': item['user_ratings_total'] if 'user_ratings_total' in item.keys() else None
                    }
                    repo['jshen97_leochans.cvsWalgreen'].insert_one(d)
        repo['jshen97_leochans.cvsWalgreen'].metadata({'complete': True})
        print(repo['jshen97_leochans.cvsWalgreen'].metadata())

        # check structure
        #for i in repo.jshen97_leochans.cvsWalgreen.find():
        #   pprint.pprint(i)

        repo.logout()

        end_time = datetime.datetime.now()

        return {"start": start_time, "end": end_time}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), start_time=None, end_time=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
        '''

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('leochans_jshen97', 'leochans_jshen97')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:jshen97_leochans#CvsWalgreen',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource_cvs = doc.entity('dat:cvs', {'prov:label': 'CVS Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        resource_wal = doc.entity('dat:walgreen', {'prov:label': 'Walgreen Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        combine = doc.activity('log:uuid' + str(uuid.uuid4()), start_time, end_time)

        doc.wasAssociatedWith(combine, this_script)
        doc.usage(combine, resource_cvs, start_time, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(combine, resource_wal, start_time, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        cvsWalgreen = doc.entity('dat:jshen97_leochans#cvsWalgreen',
                         {prov.model.PROV_LABEL: 'Combine CVS Walgreen', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(cvsWalgreen, this_script)
        doc.wasGeneratedBy(cvsWalgreen, combine, end_time)
        doc.wasDerivedFrom(cvsWalgreen, resource_cvs, combine, combine, combine)
        doc.wasDerivedFrom(cvsWalgreen, resource_wal, combine, combine, combine)

        repo.logout()

        return doc

# debug
'''
CvsWalgreen.execute()
doc = CvsWalgreen.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
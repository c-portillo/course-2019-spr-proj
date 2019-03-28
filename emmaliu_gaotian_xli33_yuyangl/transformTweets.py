import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class transformTweets(dml.Algorithm):
    contributor = 'gaotian_xli33'
    reads = ['emmaliu_gaotian_xli33_yuyangl.tweets']
    writes = ['emmaliu_gaotian_xli33_yuyangl.userLocation']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('emmaliu_gaotian_xli33_yuyangl', 'emmaliu_gaotian_xli33_yuyangl')

        # Get Tweets data
        tweetsData = repo.emmaliu_gaotian_xli33_yuyangl.tweets.find()
        locations = {}
        dataStored = []
        # Filter for user's location, project key value pairs.
        for item in tweetsData:
            if item['user']['location'] == '' or "." in item['user']['location']:
                continue

            location = item['user']['location']
            followers = item['user']['followers_count']
            friends = item['user']['friends_count']
            if location not in locations:  # Write to dictionary
                locations[location] = {'followers_count': followers, 'friends_count': friends, 'COUNT': 1}
            else:
                locations[location]['followers_count'] += followers
                locations[location]['friends_count'] += friends
                locations[location]['COUNT'] += 1
        # Calculating averages here
        for key, value in locations.items():
            dataStored.append({'location': key, 'count': value['COUNT'],
                               'avg_followers_count': value['followers_count'] / value['COUNT'],
                               'avg_friends_count': value['friends_count'] / value['COUNT']})
        # for k in dataStored.keys():
        #     print(k)
        # print(dataStored.keys())

        with open("userLocation .json", 'w') as outfile:
            json.dump(dataStored, outfile, indent=4)

        # store results into database
        repo.dropCollection("userLocation")
        repo.createCollection("userLocation")

        for i in dataStored:
            # print(i)
            repo['emmaliu_gaotian_xli33_yuyangl.userLocation'].insert(i)
        repo['emmaliu_gaotian_xli33_yuyangl.userLocation'].metadata({'complete': True})
        print(repo['emmaliu_gaotian_xli33_yuyangl.userLocation'].metadata())

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
        repo.authenticate('emmaliu_gaotian_xli33_yuyangl', 'emmaliu_gaotian_xli33_yuyangl')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/emmaliu_gaotian_xli33_yuyangl')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/emmaliu_gaotian_xli33_yuyangl')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', '')
        this_script = doc.agent('alg:emmaliu_gaotian_xli33_yuyangl#transformTweets',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:emmaliu_gaotian_xli33_yuyangl#tweets',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        transform_tweets = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transform_tweets, this_script)
        doc.usage(transform_tweets, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:calculation',
                   'ont:Query': ''
                   }
                  )
        userLocation = doc.entity('dat:emmaliu_gaotian_xli33_yuyangl#get_tweets',
                                  {prov.model.PROV_LABEL: 'tweets from Amman', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(userLocation, this_script)
        doc.wasGeneratedBy(userLocation, transform_tweets, endTime)
        doc.wasDerivedFrom(userLocation, resource, transform_tweets, transform_tweets, transform_tweets)

        repo.logout()

        return doc

# transformTweets.execute()
# doc = getTweets.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
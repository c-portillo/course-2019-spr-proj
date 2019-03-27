import sys, getopt, datetime, codecs
import DBOperations as dbo
import dml
import prov.model
import datetime
import uuid
import math
import sys

if sys.version_info[0] < 3:
    import got
else:
    import got3 as got


class TwitterDataMain(dml.Algorithm):
    contributor = 'ojhamb_runtongy_sgullett_zybu'
    reads = []
    writes = ['ojhamb_runtongy_sgullett_zybu.Tweets']

    def createTweetTuple(t):
        return (t.id, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.hashtags)

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')
        repo.dropCollection("Tweets")
        repo.createCollection("Tweets")
        #Setting Up the criteria for selecting 10000 tweets
        tweetCriteria = got.manager.TweetCriteria().setNear('Amman').setWithin('150mi').setMaxTweets(10000)
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)

        #Projecting a list of tweets
        listTweets = dbo.project(tweets, lambda t: (t.id, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.hashtags))

        #Selecting the list of tweets which have a Geo Location
        tweetsWithIDs = dbo.select(listTweets, lambda x: x[5] != '')
        print (tweetsWithIDs)

        repo.dropCollection("Tweets")
        repo.createCollection("Tweets")
        repo['ojhamb_runtongy_sgullett_zybu.Tweets'].insert_many(tweetsWithIDs)
        repo['ojhamb_runtongy_sgullett_zybu.Tweets'].metadata({'complete': True})
        print(repo['ojhamb_runtongy_sgullett_zybu.Tweets'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    def printTweet(descr='', t=None):
        print(descr)
        print("Username: %s" % t.username)
        print("Retweets: %d" % t.retweets)
        print("Text: %s" % t.text)
        print("Mentions: %s" % t.mentions)
        print("Hashtags: %s\n" % t.hashtags)

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ojhamb_runtongy_sgullett_zybu', 'ojhamb_runtongy_sgullett_zybu')

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu#Tweets',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:ojhamb_runtongy_sgullett_zybu#Tweets',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('dat:Twitter',
                              {'prov:label': 'Tweet Stage', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        getTweetStatus = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(getTweetStatus, this_script)
        doc.usage(getTweetStatus, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        tweetState = doc.entity('dat:ojhamb_runtongy_sgullett_zybu#Tweets',
                                {prov.model.PROV_LABEL: 'tweetState', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(tweetState, this_script)
        doc.wasGeneratedBy(tweetState, getTweetStatus, endTime)
        doc.wasDerivedFrom(tweetState, resource, getTweetStatus, getTweetStatus, getTweetStatus)

        repo.logout()

        return doc


TwitterDataMain.execute()
doc = Tweets.provenance()


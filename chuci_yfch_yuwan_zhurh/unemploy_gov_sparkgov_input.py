#!/usr/bin/env python
# coding: utf-8

# In[238]:


import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo

class unemploy_gov_sparkgov_input(dml.Algorithm):
    contributor = 'chuci_yfch_yuwan_zhurh'
    reads = []
    writes = ['chuci_yfch_yuwan_zhurh.unemploy', 'chuci_yfch_yuwan_zhurh.gov', 'chuci_yfch_yuwan_zhurh.sparkgov']
    @staticmethod
    #     def select(R, s):
    #         return [t for t in R if s(t)]
    #     def product(R, S):
    #         return [(t,u) for t in R for u in S]
    #     def project(R, p):
    #        return [p(t) for t in R]
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        #get the unemploy rate data
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')

        url = 'http://datamechanics.io/data/ZHU_town_unemployment.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("employ")
        repo.createCollection("unemploy")
        repo['chuci_yfch_yuwan_zhurh.unemploy'].insert_many(r)
        repo['chuci_yfch_yuwan_zhurh.unemploy'].metadata({'complete':True})
        #print(repo['chuci_yfch_yuwan_zhurh.unemploy'].metadata())
        #get the mass gov selecction rate data

        url2 =  'https://s3.amazonaws.com/media.wbur/embeds/2018/election/general-maps/data/map-ge-gov.json'
        response2 = urllib.request.urlopen(url2).read().decode("utf-8")
        r2 = json.loads(response2)
        s2 = json.dumps(r2, sort_keys=True, indent=2)
        repo.dropCollection("gov")
        repo.createCollection("gov")
        repo['chuci_yfch_yuwan_zhurh.gov'].insert_many(r2)
        repo['chuci_yfch_yuwan_zhurh.gov'].metadata({'complete':True})
        # print(repo['chuci_yfch_yuwan_zhurh.gov'].metadata())
        #get the spark goveror selection data
        url3 = 'http://datamechanics.io/data/ZHU_GovernorElection.json'
        response3 = urllib.request.urlopen(url3).read().decode("utf-8")
        r3 = json.loads(response3)
        s3 = json.dumps(r3, sort_keys=True, indent=2)
        repo.dropCollection("sparkgov")
        repo.createCollection("sparkgov")
        repo['chuci_yfch_yuwan_zhurh.sparkgov'].insert_many(r3)
        repo['chuci_yfch_yuwan_zhurh.sparkgov'].metadata({'complete':True})
        repo.logout()
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}
        #  repo['chuci_yfch_yuwan_zhurh.sparkgov'].find_one()

    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('chuci_yfch_yuwan_zhurh', 'chuci_yfch_yuwan_zhurh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://chronicdata.cdc.gov/')

        this_script = doc.agent('alg:chuci_yfch_yuwan_zhurh#getdataAlgorithm', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:onlinedata', {'prov:label':'Online Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_unemploy = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_gov = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_sparkgov = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_unemploy, this_script)
        doc.wasAssociatedWith(get_gov, this_script)
        doc.wasAssociatedWith(get_sparkgov, this_script)
        doc.usage( get_unemploy, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )
        doc.usage(get_gov, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+Lost&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )
        doc.usage(get_sparkgov, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Animal+Lost&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )
      

        unemploy = doc.entity('dat:chuci_yfch_yuwan_zhurh#unemploy', {prov.model.PROV_LABEL:'unemploy data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo( unemploy, this_script)
        doc.wasGeneratedBy( unemploy, get_unemploy, endTime)
        doc.wasDerivedFrom(unemploy, resource, get_unemploy, get_unemploy, get_unemploy)

        gov = doc.entity('dat:chuci_yfch_yuwan_zhurh#gov', {prov.model.PROV_LABEL:'gov data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(gov, this_script)
        doc.wasGeneratedBy(gov, get_gov, endTime)
        doc.wasDerivedFrom(resource, gov, get_gov, get_gov, get_gov)
        sparkgov = doc.entity('dat:chuci_yfch_yuwan_zhurh#sparkgov', {prov.model.PROV_LABEL:'sparkgov data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(sparkgov, this_script)
        doc.wasGeneratedBy(sparkgov, get_gov, endTime)
        doc.wasDerivedFrom(resource,sparkgov,  get_gov, get_gov, get_gov)

        repo.logout()
                  
        return doc



# In[239]:


# unemploy= repo['chuci_yfch_yuwan_zhurh.unemploy']
# gov=repo['chuci_yfch_yuwan_zhurh.gov']
# spark=repo['chuci_yfch_yuwan_zhurh.sparkgov']


# xx=list(spark.find({"Year": 2018}))
# repo.dropCollection("spark2018govdata")
# repo.createCollection("spark2018govdata")
# repo["spark2018govdata"].insert_many(xx)


# y1=list(unemploy.find({},{'City':1,'Rate % Dec-18':1}))
# y2=list(gov.find({'party':'GOP'},{'reportingunitname':1,'votepct':1}))


# x=select(product(y1,y2), lambda t: t[0]['City'] == t[1]['reportingunitname'])
# yyy=project(x,lambda t:{'City':t[0]['City'],'unemploy_rate':t[0]['Rate % Dec-18'],'Baker_selection_rate':t[1]['votepct']})
# repo.dropCollection("city_unemploy_baker")
# repo.createCollection("city_unemploy_baker")
# repo["city_unemploy_baker"].insert_many(yyy)



# In[240]:


# repo['chuci_yfch_yuwan_zhurh.unemploy'].find_one()


# In[234]:





# In[ ]:





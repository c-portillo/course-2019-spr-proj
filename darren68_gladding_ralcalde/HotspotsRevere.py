import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
from urllib.request import urlopen




class HotspotsRevere(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = ['darren68_gladding_ralcalde.Revere2014',
             'darren68_gladding_ralcalde.Revere2015',
             'darren68_gladding_ralcalde.Revere2016']
    writes = ['darren68_gladding_ralcalde.RevereHotspots']




    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')


        newDataSet = []

        HotspotsRevere.unionAndProjection(newDataSet, repo.darren68_gladding_ralcalde.Revere2014)
        HotspotsRevere.unionAndProjection(newDataSet, repo.darren68_gladding_ralcalde.Revere2015)
        HotspotsRevere.unionAndProjection(newDataSet, repo.darren68_gladding_ralcalde.Revere2016)


        result = HotspotsRevere.aggregate(newDataSet)
        repo.dropCollection("RevereHotspots")
        repo.createCollection("RevereHotspots")
        repo['darren68_gladding_ralcalde.RevereHotspots'].insert_many(result)
        repo['darren68_gladding_ralcalde.RevereHotspots'].metadata({'complete':True})


        repo.logout()
        endTime = datetime.datetime.now()

        return {"start" : startTime, "end" :endTime}






    '''
    Project the xy coordinate and manner of collision, add each document 
    to the new data set -- same as a unions
    
    '''
    @staticmethod
    def unionAndProjection(newDataSet, collection):
        for doc in collection.find():
            newDoc = {}
            x = doc['xcoordinate'].split('.')[0]
            y = doc['ycoordinate'].split('.')[0]
            xy = x + ", " + y
            newDoc['xycoordinate'] = xy
            newDoc['mannerofcollision'] = doc['mannerofcollision']
            newDataSet.append(newDoc)





    @staticmethod
    def aggregate(R):
        newDataSet = []
        keys = {r['xycoordinate'] for r in R}

        for key in keys:
            newDoc = {'xycoordinate': key}
            values =[]      #we will be adding the manner of collison strings here


            #will get the list of values associated with a key
            for doc in R:
                if doc['xycoordinate'] == key:
                    values.append(doc['mannerofcollision'])


            #now I need to perform the function of those values
            mannersOfCollision = set(values)

            if len(values) > 1:
                for m in mannersOfCollision:
                    count = 0
                    for v in values:
                        if v == m:
                            count += 1
                    newDoc[m] = count
                newDataSet.append(newDoc)

        return newDataSet






    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.


        # Agent, entity, activity
        this_script = doc.agent('alg:darren68_gladding_ralcalde#HotspotsRevere',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        Revere2016_data = doc.entity('dat:darren68_gladding_ralcalde#Revere2016',
                              {'prov:label': 'Revere 2016 data', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})
        Revere2015_data = doc.entity('dat:darren68_gladding_ralcalde#Revere2015',
                                     {'prov:label': 'Revere 2015 data', prov.model.PROV_TYPE: 'ont:DataSet',
                                      'ont:Extension': 'json'})
        Revere2014_data = doc.entity('dat:darren68_gladding_ralcalde#Revere2014',
                                     {'prov:label': 'Revere 2014 data', prov.model.PROV_TYPE: 'ont:DataSet',
                                      'ont:Extension': 'json'})
        # Activity
        get_RevereData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_RevereData, this_script)

        doc.usage(get_RevereData, Revere2016_data, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   }
                  )
        doc.usage(get_RevereData, Revere2015_data, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   }
                  )
        doc.usage(get_RevereData, Revere2014_data, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   }
                  )
        RevereHotspots = doc.entity('dat:darren68_gladding_ralcalde#RevereHotspots',
                             {prov.model.PROV_LABEL: "Collision Hotspots in Revere"
                                 , prov.model.PROV_TYPE: 'ont:DataSet'})
        createHotspotsData = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(createHotspotsData, this_script)
        doc.wasAttributedTo(RevereHotspots, this_script)
        doc.wasGeneratedBy(RevereHotspots, createHotspotsData, endTime)
        doc.usage(createHotspotsData, Revere2016_data, startTime, None,
                  {prov.model.PROV_LABEL: "Used Revere2016 data to help compute hotspots"
                      , prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(createHotspotsData, Revere2015_data, startTime, None,
                  {prov.model.PROV_LABEL: "Used Revere2015 data to help compute hotspots"
                      , prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(createHotspotsData, Revere2014_data, startTime, None,
                  {prov.model.PROV_LABEL: "Used Revere2014 data to compute hotspots"
                      , prov.model.PROV_TYPE: 'ont:Computation'})

        doc.wasDerivedFrom(RevereHotspots, Revere2016_data, createHotspotsData, createHotspotsData, createHotspotsData)
        doc.wasDerivedFrom(RevereHotspots, Revere2015_data, createHotspotsData, createHotspotsData, createHotspotsData)
        doc.wasDerivedFrom(RevereHotspots, Revere2014_data, createHotspotsData, createHotspotsData, createHotspotsData)

        repo.logout()
        return doc



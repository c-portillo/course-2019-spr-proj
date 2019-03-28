import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
from urllib.request import urlopen


class Revere2000(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = []
    writes = ['darren68_gladding_ralcalde.Revere2000']

    @staticmethod
    def execute(trial=False):
        '''Retrieve data set of crashes in Revere for the year 2000 and store it in Mongo'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')

        # this is the url of the dataset
        url = 'http://datamechanics.io/data/darren68_gladding_ralcalde/REVERE2000updated.csv'

        # load the url and read it
        response = urllib.request.urlopen(url)
        file = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter=',')

        # skip the headers
        next(file, None)

        dictList = []
        isNotFirst = False

        # iterate through each row in the file and assign each element to the corresponding field in the dictionary
        for row in file:
            dic = {}
            dic['Town'] = row[0]
            dic['Crash_Date'] = row[1]
            dic['Crash_Time'] = row[2]
            dic['Crash_Type'] = row[3]
            dic['Total_Vehicles'] = row[4]
            dic['Total_Injured'] = row[5]
            dic['Total_Fatals'] = row[6]
            dic['Veh1_Dir'] = row[7]
            dic['Veh2_Dir'] = row[8]
            dic['Collision_manner'] = row[9]
            dic['Object_hit'] = row[10]
            dic['Collision_with'] = row[11]
            dic['Road_Surface'] = row[12]
            dic['Lighting'] = row[13]
            dic['Weather'] = row[14]
            dic['Street'] = row[15]
            dic['Intersection'] = row[16]
            dic['Feet_From'] = row[17]
            dic['Dir_From'] = row[18]
            dictList.append(dic)

        repo.dropCollection("Revere2000")
        repo.createCollection("Revere2000")
        repo['darren68_gladding_ralcalde.Revere2000'].insert_many(dictList)
        repo['darren68_gladding_ralcalde.Revere2000'].metadata({'complete': True})

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
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        # doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        # Agent, entity, activity
        this_script = doc.agent('alg:darren68_gladding_ralcalde#Revere2000',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        # Resource = All Towns Data
        resource = doc.entity('dat:darren68_gladding_ralcalde',
                              {'prov:label': 'Crashes', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        # Activity
        get_crashes = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_crashes, this_script)

        doc.usage(get_crashes, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': ''
                   }
                  )

        crashes = doc.entity('dat:darren68_gladding_ralcalde#Revere2000',
                             {prov.model.PROV_LABEL: 'Crashes', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crashes, this_script)
        doc.wasGeneratedBy(crashes, get_crashes, endTime)
        doc.wasDerivedFrom(crashes, resource, get_crashes, get_crashes, get_crashes)

        repo.logout()

        return doc

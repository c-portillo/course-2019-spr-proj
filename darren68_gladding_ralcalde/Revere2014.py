import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
from urllib.request import urlopen


class Revere2014(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = []
    writes = ['darren68_gladding_ralcalde.Revere2014']

    @staticmethod
    def execute(trial=False):
        '''Retrieve data set of crashes in Revere for the year 2014 and store it in Mongo'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')

        # this is the url of the dataset
        url = 'http://datamechanics.io/data/darren68_gladding_ralcalde/REVERE2014updated.csv'

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
            dic['crashnumber'] = row[0]
            dic['citytownname'] = row[1]
            dic['crashdate'] = row[2]
            dic['crashtime'] = row[3]
            dic['crashseverity'] = row[4]
            dic['numberofvehicles'] = row[5]
            dic['totalnonfatalinjuries'] = row[6]
            dic['totalfatalinjuries'] = row[7]
            dic['mannerofcollision'] = row[8]
            dic['vehicleactionpriortocrash'] = row[9]
            dic['vehicletraveldirections'] = row[10]
            dic['mostharmfulevents'] = row[11]
            dic['vehicleconfiguration'] = row[12]
            dic['roadsurfacecondition'] = row[13]
            dic['ambientlight'] = row[14]
            dic['weathercondition'] = row[15]
            dic['atroadwayintersection'] = row[16]
            dic['distancefromnearestroadwayinters'] = row[17]
            dic['distancefromnearestmilemarker'] = row[18]
            dic['distancefromnearestexit'] = row[19]
            dic['distancefromnearestlandmark'] = row[20]
            dic['nonmotoristtype'] = row[21]
            dic['xcoordinate'] = row[22]
            dic['ycoordinate'] = row[23]

            dictList.append(dic)

        repo.dropCollection("Revere2014")
        repo.createCollection("Revere2014")
        repo['darren68_gladding_ralcalde.Revere2014'].insert_many(dictList)
        repo['darren68_gladding_ralcalde.Revere2014'].metadata({'complete': True})

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
        this_script = doc.agent('alg:darren68_gladding_ralcalde#Revere2014',
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

        crashes = doc.entity('dat:darren68_gladding_ralcalde#Revere2014',
                             {prov.model.PROV_LABEL: 'Crashes', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crashes, this_script)
        doc.wasGeneratedBy(crashes, get_crashes, endTime)
        doc.wasDerivedFrom(crashes, resource, get_crashes, get_crashes, get_crashes)

        repo.logout()

        return doc
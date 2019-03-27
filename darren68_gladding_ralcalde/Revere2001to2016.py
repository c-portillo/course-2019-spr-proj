import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
from urllib.request import urlopen


class Revere2001to2016(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = []
    writes = ['darren68_gladding_ralcalde.Revere2001to2016']

    @staticmethod
    def execute(trial=False):
        '''Retrieve data set of crashes in Revere for the year 2001 to 2016 and store it in Mongo'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')

        # this is the url of the dataset
        url = 'http://datamechanics.io/data/darren68_gladding_ralcalde/REVERE2001to2016updated.csv'

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
            dic['crashdate'] = row[1]
            dic['crashtime'] = row[2]
            dic['crashhour'] = row[3]
            dic['citytown'] = row[4]
            dic['locality'] = row[5]
            dic['rpaabbreviation'] = row[6]
            dic['masshighwaydistrict'] = row[7]
            dic['crashseverity'] = row[8]
            dic['maximuminjuryseverityreported'] = row[9]
            dic['numberofnonfatalinjuries'] = row[10]
            dic['numberoffatalinjuries'] = row[11]
            dic['numberofvehicles'] = row[12]
            dic['mannerofcollision'] = row[13]
            dic['vehicleactionpriortocrash'] = row[14]
            dic['vehicletraveldirections'] = row[15]
            dic['firstharmfulevent'] = row[16]
            dic['firstharmfuleventlocation'] = row[17]
            dic['mostharmfulevents'] = row[18]
            dic['vehiclesequenceofevents'] = row[19]
            dic['vehicleconfiguration'] = row[20]
            dic['fmscareportable'] = row[21]
            dic['ageofdriveryoungestknown'] = row[22]
            dic['ageofdriveroldestknown'] = row[23]
            dic['drivercontributingcodes'] = row[24]
            dic['nonmotoristtype'] = row[25]
            dic['nonmotoristaction'] = row[26]
            dic['nonmotoristlocation'] = row[27]
            dic['hitrun'] = row[28]
            dic['roadsurface'] = row[29]
            dic['ambientlight'] = row[30]
            dic['weathercondition'] = row[31]
            dic['streetnumber'] = row[32]
            dic['roadway'] = row[33]
            dic['distanceanddirectionfromintersec'] = row[34]
            dic['nearintersectionroadway'] = row[35]
            dic['exitroute'] = row[36]
            dic['distanceanddirectionfromexitnumb'] = row[37]
            dic['exitnumber'] = row[38]
            dic['milemarkerroute'] = row[39]
            dic['distanceanddirectionfrommilemark'] = row[40]
            dic['milemarker'] = row[41]
            dic['landmark'] = row[42]
            dic['distanceanddirectionfromlandmark'] = row[43]
            dic['trafficway'] = row[44]
            dic['speedlimit'] = row[45]
            dic['roadwayintersectiontype'] = row[46]
            dic['trafficcontroldevicetype'] = row[47]
            dic['trafficdevicefunctioning'] = row[48]
            dic['policeagency'] = row[49]
            dic['linkedrifunctionalclassification'] = row[50]
            dic['linkedriaccesscontrol'] = row[51]
            dic['linkedritollroad'] = row[52]
            dic['linkedrijurisdiction'] = row[53]
            dic['linkedrinumberoftravellanes'] = row[54]
            dic['linkedriopposingnumberoftravella'] = row[55]
            dic['linkedristreetname'] = row[56]
            dic['linkedristreetoperation'] = row[57]
            dic['linkedrifacilitytype'] = row[58]
            dic['linkedrispeedlimit'] = row[59]
            dic['linkedriurbantype'] = row[60]
            dic['linkedriurbanizedarea'] = row[61]
            dic['linkedriurbanlocationtype'] = row[62]
            dic['linkedriaveragedailytraffic'] = row[63]
            dic['linkedriyearofadt'] = row[64]
            dic['linkedritruckroute'] = row[65]
            dic['schoolbusrelated'] = row[66]
            dic['isgeocoded'] = row[67]
            dic['geocodingmethod'] = row[68]
            dic['x'] = row[69]
            dic['y'] = row[70]
            dic['crashstatus'] = row[71]
            dic['roadsegmentid'] = row[72]
            dic['county'] = row[73]
            dic['rmvdocument'] = row[74]
            dic['driverdistractedby'] = row[75]
            dic['ageofnonmotoristyoungestknown'] = row[76]
            dic['ageofnonmotoristoldestknown'] = row[77]
            dic['reportids'] = row[78]
            dic['federalfunctionalclassification'] = row[79]
            dic['roadwaycontributingcode'] = row[80]
            dictList.append(dic)

        repo.dropCollection("Revere2001to2016")
        repo.createCollection("Revere2001to2016")
        repo['darren68_gladding_ralcalde.Revere2001to2016'].insert_many(dictList)
        repo['darren68_gladding_ralcalde.Revere2001to2016'].metadata({'complete': True})

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
        this_script = doc.agent('alg:darren68_gladding_ralcalde#Revere2001to2016',
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

        crashes = doc.entity('dat:darren68_gladding_ralcalde#Revere2001to2016',
                             {prov.model.PROV_LABEL: 'Crashes', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crashes, this_script)
        doc.wasGeneratedBy(crashes, get_crashes, endTime)
        doc.wasDerivedFrom(crashes, resource, get_crashes, get_crashes, get_crashes)

        repo.logout()

        return doc

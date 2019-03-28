import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
from bson.objectid import ObjectId

class nonBusRiders(dml.Algorithm):
    contributor = 'ido_jconstan_jeansolo_suitcase'
    reads = ['ido_jconstan_jeansolo_suitcase.bu_transportation_study',
             'ido_jconstan_jeansolo_suitcase.property_data']
    writes = ['ido_jconstan_jeansolo_suitcase.PropertyValueNonRiders']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ido_jconstan_jeansolo_suitcase', 'ido_jconstan_jeansolo_suitcase')

        # create new things
        repo.dropCollection("PropertyValueNonRiders")
        repo.createCollection("PropertyValueNonRiders")

        #r = repo.ido_jconstan_jeansolo_suitcase.bu_transportation_study.find()
        # OBTAINING FIRST DATASET [Bu Transportation Study]
        url = 'http://datamechanics.io/data/ido_jconstan_jeansolo_suitcase/bu_transportation_study.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        for i in r:
            i['Address'] = i['Address'].upper()

            if "STREET" in i['Address']:
                i['Address'] = i['Address'].replace("STREET", "ST")
            if "PLACE" in i['Address']:
                i['Address'] = i['Address'].replace("PLACE", "PL")
            if "TERRACE" in i['Address']:
                i['Address'] = i['Address'].replace("TERRACE", "TER")
            if "AVENUE" in i['Address']:
                i['Address'] = i['Address'].replace("AVENUE", "AVE")
            if "CIRCLE" in i['Address']:
                i['Address'] = i['Address'].replace("CIRCLE", "CIR")
            if "COURT" in i['Address']:
                i['Address'] = i['Address'].replace("COURT", "CT")
            if "LANE" in i['Address']:
                i['Address'] = i['Address'].replace("LANE", "LN")
            if "ROAD" in i['Address']:
                i['Address'] = i['Address'].replace("ROAD", "RD")
            if "PARK" in i['Address']:
                i['Address'] = i['Address'].replace("PARK", "PK")

        #r1 = repo.ido_jconstan_jeansolo_suitcase.property_data.find()
        # OBTAINING SECOND DATA SET [Spark Property Data]
        url = 'http://datamechanics.io/data/ido_jconstan_jeansolo_suitcase/property_data.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r1 = json.loads(response)
        for i in r1:
            i['Address 1'] = i['Address 1'].upper()

            if "STREET" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("STREET", "ST")
            if "PLACE" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("PLACE", "PL")
            if "TERRACE" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("TERRACE", "TER")
            if "AVENUE" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("AVENUE", "AVE")
            if "CIRCLE" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("CIRCLE", "CIR")
            if "COURT" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("COURT", "CT")
            if "LANE" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("LANE", "LN")
            if "ROAD" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("ROAD", "RD")
            if "PARK" in i['Address 1']:
                i['Address 1'] = i['Address 1'].replace("PARK", "PK")

        # Transform 1
        # Get the students who do NOT ride the bus
        notBusRiders = []
        tempFlag = False
        for x in r1:
            for y in r:
                # if the student does ride the bus
                if x['Address 1'] in y['Address']:
                    tempFlag = True
            if (tempFlag == False):
                notBusRiders.append(x)
            else:
                tempFlag = False
        
        # Get the house price of students who do NOT ride the bus
        nbrHouseValue = []
        for x in notBusRiders:
            nbrHouseValue.append({"Address 1": x['Address 1'], "Assessed Total":x['Assessed Total']})

        repo['ido_jconstan_jeansolo_suitcase.PropertyValueNonRiders'].insert_many(nbrHouseValue)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ido_jconstan_jeansolo_suitcase', 'ido_jconstan_jeansolo_suitcase')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('dbg', 'https://data.boston.gov/dataset/greenhouse-gas-emissions/resource/')
        doc.add_namespace('dbg2', 'https://data.boston.gov/dataset/public-works-active-work-zones/resource/')
        doc.add_namespace('oda', 'https://opendata.arcgis.com/datasets/')



        this_script = doc.agent('alg:ido_jconstan_jeansolo_suitcase#nonBusRiders', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_nonBusRiders = doc.entity('dat:nonBusRiders', {'prov:label':'Non Bus Riders', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_nonBusRiders = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_nonBusRiders, this_script)
        doc.usage(get_nonBusRiders, resource_nonBusRiders, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        non_Bus_Riders = doc.entity('dat:ido_jconstan_jeansolo_suitcase#non_Bus_Riders', {prov.model.PROV_LABEL:'Traffic Count', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(non_Bus_Riders, this_script)
        doc.wasGeneratedBy(non_Bus_Riders, get_nonBusRiders, endTime)
        doc.wasDerivedFrom(non_Bus_Riders, resource_nonBusRiders, get_nonBusRiders, get_nonBusRiders, get_nonBusRiders)
        
        repo.logout()
                  
        return doc

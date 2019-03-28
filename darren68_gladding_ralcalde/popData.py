import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv
import io
from urllib.request import urlopen


class popData(dml.Algorithm):
    contributor = 'darren68_gladding_ralcalde'
    reads = []
    writes = ['darren68_gladding_ralcalde.popData']

    @staticmethod
    def execute(trial = False):
        '''Retrieve data set of population data store it in Mongo'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')

        #this is the url of the dataset
        url = 'http://datamechanics.io/data/darren68_gladding_ralcalde/popData.csv'

        #load the url and read it
        response = urllib.request.urlopen(url)
        file = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter = ',')

        #skip the headers
        next(file, None)
        
        dictList = []
        isNotFirst = False

        #iterate through each row in the file and assign each element to the corresponding field in the dictionary
        for row in file:
            dic = {}
            dic['year'] = row[0]
            dic['datanum'] = row[1]
            dic['serial'] = row[2]
            dic['cbserial'] = row[3]
            dic['hhwt'] = row[4]
            dic['statefip'] = row[5]
            dic['countyfip'] = row[6]
            dic['gq'] = row[7]
            dic['pernum'] = row[8]
            dic['PersonWeight'] = row[9]
            
            dictList.append(dic)


        repo.dropCollection("popData")
        repo.createCollection("popData")
        repo['darren68_gladding_ralcalde.popData'].insert_many(dictList)
        repo['darren68_gladding_ralcalde.popData'].metadata({'complete':True})
        print(repo['darren68_gladding_ralcalde.popData'].metadata())



        repo.logout()
        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('darren68_gladding_ralcalde', 'darren68_gladding_ralcalde')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        #doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        #Agent, entity, activity
        this_script = doc.agent('alg:darren68_gladding_ralcalde#popData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        #Resource = All Towns Data
        resource = doc.entity('dat:darren68_gladding_ralcalde', {'prov:label':'Revere Population', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        
        #Activity
        get_pop = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_pop, this_script)

        doc.usage(get_pop, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        pop = doc.entity('dat:darren68_gladding_ralcalde#popData', {prov.model.PROV_LABEL:'Revere Population', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(pop, this_script)
        doc.wasGeneratedBy(pop, get_pop, endTime)
        doc.wasDerivedFrom(pop, resource, get_pop, get_pop, get_pop)

        repo.logout()
                  
        return doc

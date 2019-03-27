import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import copy
import pandas as pd
from census import Census
from us import states

class transformDem(dml.Algorithm):
    contributor = 'misn15'
    reads = ['misn15.waste', 'misn15.zipcode', 'misn15.income']
    writes = ['misn15.waste_income']

    @staticmethod
    def execute(trial = False):
        '''Retrieve crime data for city of Boston'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('misn15', 'misn15')

        zipcodes = []
        zipcodes = repo['misn15.zipcodes'].find()
        zipcodes = [x for x in zipcodes]

        waste = []
        waste = repo['misn15.waste'].find()
        waste = copy.deepcopy(waste)

        income = []
        income = repo['misn15.income'].find()
        data_pd =  pd.DataFrame(income)

        # add columns together
        data_pd['full_tract'] = data_pd[['state', 'county', 'tract']].apply(lambda x: ''.join(x), axis=1)
        data_pd['zipcode'] = -1
        
        # match median incomes to zipcodes; some zipcodes will have multiple median incomes
        zips = {}
        for i in range(len(data_pd)):
            for j in range(len(zipcodes)):
                if int(data_pd.iloc[i]['full_tract']) == zipcodes[j]['tract']:
                    if zipcodes[j]['zip'] not in zips and data_pd.iloc[i]['B06011_001E'] != -666666666.0:
                        zips[zipcodes[j]['zip']] = [str(data_pd.iloc[i]['B06011_001E'])]
                    elif data_pd.iloc[i]['B06011_001E'] != -666666666.0:
                        zips[zipcodes[j]['zip']].append(str(data_pd.iloc[i]['B06011_001E']))

        # for each zipcode get number of average median incomes and their sum to find the mean; projection and aggregation    
        incomes_list = []
        sum_incomes = 0       
        for key, value in zips.items():
            sum_incomes = 0
            for y in value:
                sum_incomes += float(y)
            incomes_list += [[key, len(value), sum_incomes]]

        # get mean income for each zipcode
        
        mean_incomes = [[x[0], x[2]/x[1]] for x in incomes_list]
                            
        # product between waste and median income
        product = []
        for row in waste:
            for i in range(len(mean_incomes)):
                product += [[row, mean_incomes[i]]]

        # selection and projection
        projection = [(x[0]['Address'], x[0]['ZIP Code'], x[1][1]) for x in product if str(x[1][0]) == x[0]['ZIP Code']]

        # aggregate number of waste sites for each zip code
        keys = []
        for x in projection:
            keys += [x[1]]
        keys = set(keys)

        agg_waste = [[key, sum([1 for x in projection if x[1] == key])] for key in keys]

        # add mean incomes to zipcodes
        for x in agg_waste:
            for y in mean_incomes:
                if x[0] == str(y[0]):
                    x += [round(y[1], 2)]            

                    
        repo.dropCollection("misn15.waste_income")
        repo.createCollection("misn15.waste_income")

        for x in agg_waste:
            entry = {'Zip code': x[0], '# of Waste Sites': x[1], 'Median Income': x[2]}
            repo['misn15.waste_income'].insert_one(entry)
         

        repo['misn15.waste_income'].metadata({'complete':True})
        print(repo['misn15.waste_income'].metadata())

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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('waste', 'http://datamechanics.io/data/misn15/hwgenids.json') 
        doc.add_namespace('zipcodes', 'http://datamechanics.io/data/zip_tracts.json')
        doc.add_namespace('income', 'http://datamechanics.io/')
        
               
        this_script = doc.agent('alg:misn15#transformDem', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:zipcodes', {'prov:label':'Boston Zip Codes', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})                  
        resource2 = doc.entity('dat:income', {'prov:label':'Median Income', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource3 = doc.entity('dat:waste', {'prov:label':'Waste Sites', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
         
        get_zips = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_zips, this_script)
        doc.usage(get_zips, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                     }
                  )      
        doc.usage(get_zips, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )
        doc.usage(get_zips, resource3, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )
        zipcodes = doc.entity('dat:misn15#zipcodes', {prov.model.PROV_LABEL:'Boston Crime', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(zipcodes, this_script)
        doc.wasGeneratedBy(zipcodes, get_zips, endTime)
        doc.wasDerivedFrom(zipcodes, resource, get_zips, get_zips, get_zips)

        income = doc.entity('dat:misn15#income', {prov.model.PROV_LABEL:'Boston Crime', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(income, this_script)
        doc.wasGeneratedBy(income, get_zips, endTime)
        doc.wasDerivedFrom(income, resource2, get_zips, get_zips, get_zips)

        waste = doc.entity('dat:misn15#waste', {prov.model.PROV_LABEL:'Boston Crime', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(waste, this_script)
        doc.wasGeneratedBy(waste, get_zips, endTime)
        doc.wasDerivedFrom(waste, resource3, get_zips, get_zips, get_zips)


                  
        return doc


transformDem.execute()
doc = transformDem.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof

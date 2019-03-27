import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pprint

class mergeIncomePoverty(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = ['henryhcy_wangyp.income','henryhcy_wangyp.poverty']
    writes = ['henryhcy_wangyp.IncomePoverty']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        income = repo['henryhcy_wangyp.income']
        poverty = repo['henryhcy_wangyp.poverty']
        
        info = []
        for i in income.find():
            i = i.copy()
            temp = poverty.find_one({"Region":i['Region']})
            if temp:
                i['population'] = temp['Total population for whom\npoverty status is determined']
                i['Total in poverty'] = temp['Total in poverty']
                i['Poverty rate'] = temp['Poverty rate']
            else:
                i['population'] = temp['N/A']
                i['Total in poverty'] = temp['N/A']
                i['Poverty rate'] = temp['N/A']
            info.append(i)


        repo.dropCollection("henryhcy_wangyp.IncomePoverty")
        repo.createCollection("henryhcy_wangyp.IncomePoverty")
        repo['henryhcy_wangyp.IncomePoverty'].insert_many(info)
        repo['henryhcy_wangyp.IncomePoverty'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.IncomePoverty'].metadata())


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
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/ybavishi#') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/ybavishi#') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg: mergeIncomePoverty', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:income', {'prov:label':'income', prov.model.PROV_TYPE:'ont:DataResource'})
        resource2 = doc.entity('dat:poverty', {'prov:label':'poverty', prov.model.PROV_TYPE:'ont:DataResource'})
        get_prices = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        
        doc.wasAssociatedWith(get_prices, this_script)

        doc.usage(get_prices, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        doc.usage(get_prices, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )


        prices = doc.entity('dat:areaIncomesData', {prov.model.PROV_LABEL:'Household Incomes in Rent Areas', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(prices, this_script)
        doc.wasGeneratedBy(prices, get_prices, endTime)
        doc.wasDerivedFrom(prices, resource, get_prices, get_prices, get_prices)
        doc.wasDerivedFrom(prices, resource2, get_prices, get_prices, get_prices)


      
        repo.logout()
                  
        return doc

#mergeIncomePoverty.execute()
#doc = mergeIncomePoverty.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))

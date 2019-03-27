import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pprint

class mergeRestaurantInspection(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = ['henryhcy_wangyp.restaurant','henryhcy_wangyp.inspection']
    writes = ['henryhcy_wangyp.RestaurantInspection']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        print('4')

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        restaurant = repo['henryhcy_wangyp.restaurant']
        inspection = repo['henryhcy_wangyp.inspection']
        
        newdata = []
        for i in restaurant.find():
            i = i.copy()
        
            temps = inspection.find({'property_id':i['property_id']})
            if temps:
                v1 = 0
                v2 = 0
                v3 = 0
                for temp in temps:
                    if temp['violation_level'] == '*':
                        v1 += 1
                    elif temp['violation_level'] == '**':
                        v2 += 1
                    elif temp['violation_level'] == '***':
                        v3+=1
                    i['v_1'] = v1
                    i['v_2'] = v2
                    i['v_3'] = v3

            else:
                i['v_1'] = 'N/A'
                i['v_2'] = 'N/A'
                i['v_3'] = 'N/A'
            newdata.append(i)


        repo.dropCollection("henryhcy_wangyp.RestaurantInspection")
        repo.createCollection("henryhcy_wangyp.RestaurantInspection")
        repo['henryhcy_wangyp.RestaurantInspection'].insert_many(newdata)
        repo['henryhcy_wangyp.RestaurantInspection'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.RestaurantInspection'].metadata())


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

        this_script = doc.agent('alg: mergeRestaurantInspection', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:restaurant', {'prov:label':'restaurant', prov.model.PROV_TYPE:'ont:DataResource'})
        resource2 = doc.entity('dat:insepection', {'prov:label':'insepection', prov.model.PROV_TYPE:'ont:DataResource'})
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


        prices = doc.entity('dat:RestaurantInspection', {prov.model.PROV_LABEL:'restaurant violation level', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(prices, this_script)
        doc.wasGeneratedBy(prices, get_prices, endTime)
        doc.wasDerivedFrom(prices, resource, get_prices, get_prices, get_prices)
        doc.wasDerivedFrom(prices, resource2, get_prices, get_prices, get_prices)


      
        repo.logout()
                  
        return doc

#mergeRestaurantInspection.execute()
#doc = mergeRestaurantInspection.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))

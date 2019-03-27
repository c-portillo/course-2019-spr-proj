import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import csv 
import io
#get the data about neighborhoods

class restaurant(dml.Algorithm):
    contributor = 'henryhcy_wangyp'
    reads = []
    writes = ['henryhcy_wangyp.restaurant']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
    

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('henryhcy_wangyp', 'henryhcy_wangyp')
        url = 'https://data.boston.gov/dataset/5e4182e3-ba1e-4511-88f8-08a70383e1b6/resource/f1e13724-284d-478c-b8bc-ef042aa5b70b/download/tmpksffaw5l.csv'        
        response = urllib.request.urlopen(url)
        cr = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter = ',')
        # parse the data as following
        rs = []
        i = 0
        for row in cr:
                if(i != 0):
                    dic = {}
                    dic['restaurantName'] = row[0]
                    dic['Address'] = row[2]
                    dic['city'] = row[3]
                    dic['state'] = row[4]
                    dic['Descript'] = row[8]
                    dic['property_id'] = row[11]
                    x,y = row[12].split(",")
                    dic['Y'] = x[1:]
                    dic['X'] = y[:-1]
                    rs.append(dic)
                i += 1
        repo.dropCollection("restaurant")
        repo.createCollection("restaurant")
        repo['henryhcy_wangyp.restaurant'].insert_many(rs)
        repo['henryhcy_wangyp.restaurant'].metadata({'complete':True})
        print(repo['henryhcy_wangyp.restaurant'].metadata())
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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'hhttp://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:henryhcy_wangyp#restaurant', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:5e4182e3-ba1e-4511-88f8-08a70383e1b6/resource/f1e13724-284d-478c-b8bc-ef042aa5b70b/download/tmpksffaw5l.csv', {'prov:label':'restaurant information', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_restaurant = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_restaurant, this_script)
        doc.usage(get_restaurant, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=restaurant&$select=name,address,city,state,location,OPEN_DT'
                  }
                  )
        

        restaurant = doc.entity('dat:henryhcy_wangyp#restaurant', {prov.model.PROV_LABEL:'restaurant', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(restaurant, this_script)
        doc.wasGeneratedBy(restaurant, get_restaurant, endTime)
        doc.wasDerivedFrom(restaurant, resource, get_restaurant, get_restaurant, get_restaurant)

        

        repo.logout()
                  
        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import math

class reWeatherParking(dml.Algorithm):
    contributor = 'ctrinh'
    reads = ['ctrinh.weather15', 'ctrinh.parking']
    writes = ['ctrinh.reWeatherParking']

    @staticmethod
    def execute(trial = False):
        '''Transforms two datasets.'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ctrinh', 'ctrinh')

        l1 = list(repo.ctrinh.weather15.find())
        l2 = list(repo.ctrinh.parking.find())
        # print(l1)
        # print(l2[0]['result']['records'])

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

        # Perform a selection on the weather data to only return monthly values.
        # print(l1[0]['MonthlyMeanTemperature'].is_integer())
        # print(type(l1))

        l1s = []

        for tuple in l1:
            if math.isnan(tuple['MonthlyMeanTemperature']) == False:
                l1s.append(tuple)

        # print(l1s)


        # Aggregate the number of parked cars per month across all lots.
        d1 = dict.fromkeys(months, 0)
        # print(d1)
        # print('starting iterate')

        for lot in l2[0]['result']['records']:
            # print(lot)
            for field in lot:
                # print(lot[field])
                if field in months:
                    # print(lot[field])
                    if lot[field] != None:
                        # print('yes')
                        # print(field)
                        # print(d1[field], lot[field])
                        d1[field] += int(lot[field])

        # print(d1)

        # Union the two datasets together after transforming the weather date keys into months.
        r = dict.fromkeys(months, {})

        d1l = []
        for month in d1.keys():
            d1l.append(d1[month])
        # print(d1l)

        # ll = ['ParkedCars'] * 12
        # print(ll)
        # d1d = dict.fromkeys(ll, 0)
        #
        # for value in range(len(d1l)):
        #     d1d[months][value] = d1l[value]

        for i in range(len(months)):
            t = {}
            t['ParkedCars'] = d1l[i]
            t['MonthlyMaximumTemperature'] = l1s[i]['MonthlyMaximumTemperature']
            t['MonthlyTotalLiquidPrecipitation'] = l1s[i]['MonthlyTotalLiquidPrecipitation']
            t['MonthlyTotalSnowfall'] = l1s[i]['MonthlyTotalSnowfall']
            r[months[i]] = t
        # r['January'] = {'A':5, 'B': 7}
        # print(r)

        repo.dropCollection("reWeatherParking")
        repo.createCollection("reWeatherParking")
        repo['ctrinh.reWeatherParking'].insert_many([r])
        repo['ctrinh.reWeatherParking'].metadata({'complete':True})
        print(repo['ctrinh.reWeatherParking'].metadata())

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
        repo.authenticate('ctrinh', 'ctrinh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('dbg', 'https://data.boston.gov/api/3/action/')

        this_script = doc.agent('alg:ctrinh#reWeatherParking', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        # resource = doc.entity('dbg:datastore_search', {'prov:label':'Park Boston Monthly 2015', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        parking = doc.entity('dat:ctrinh#parking', {prov.model.PROV_LABEL:'Parking Usage', prov.model.PROV_TYPE:'ont:DataSet'})
        weather = doc.entity('dat:ctrinh#weather15', {prov.model.PROV_LABEL:'Weather 2015', prov.model.PROV_TYPE:'ont:DataSet'})
        get_reWeatherParking = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_reWeatherParking, this_script)
        doc.usage(get_reWeatherParking, parking, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'}
                  )
        doc.usage(get_reWeatherParking, weather, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'}
                  )

        reWeatherParking = doc.entity('dat:ctrinh#reWeatherParking', {prov.model.PROV_LABEL:'Monthly Weather and Parking Usage', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(reWeatherParking, this_script)
        doc.wasGeneratedBy(reWeatherParking, get_reWeatherParking, endTime)
        doc.wasDerivedFrom(reWeatherParking, parking, get_reWeatherParking, get_reWeatherParking, get_reWeatherParking)
        doc.wasDerivedFrom(reWeatherParking, weather, get_reWeatherParking, get_reWeatherParking, get_reWeatherParking)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
reWeatherParking.execute()
doc = reWeatherParking.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

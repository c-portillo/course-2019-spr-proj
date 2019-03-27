import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import math

class reWeatherUber(dml.Algorithm):
    contributor = 'ctrinh'
    reads = ['ctrinh.weather18', 'ctrinh.uber']
    writes = ['ctrinh.reWeatherUber']

    @staticmethod
    def execute(trial = False):
        '''Transforms two datasets.'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ctrinh', 'ctrinh')

        l1 = list(repo.ctrinh.weather18.find())
        l2 = list(repo.ctrinh.uber.find())

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November']

        # Perform a selection on the weather data to only return monthly values.
        l1s = []
        for tuple in l1:
            if math.isnan(tuple['MonthlyMeanTemperature']) == False:
                l1s.append(tuple)

        # print(l1s)
        # print(len(l1s))

        # Perform an aggregation on Uber mean travel times by the month key.
        # print(l2[0])
        d1 = dict.fromkeys(months, 0)

        for i in range(len(months)):
            for tuple in l2:
                if (tuple['month']-1) == i:
                    # print(tuple['month'], i)
                    d1[months[i]] += tuple['mean_travel_time']

        # print(d1)
        # print(d1)
        # print('starting iterate')

        # for lot in l2[0]['result']['records']:
        #     # print(lot)
        #     for field in lot:
        #         # print(lot[field])
        #         if field in months:
        #             # print(lot[field])
        #             if lot[field] != None:
        #                 # print('yes')
        #                 # print(field)
        #                 # print(d1[field], lot[field])
        #                 d1[field] += int(lot[field])

        # print(d1)

        # Union the two datasets together after transforming the weather date keys into months.
        r = dict.fromkeys(months, {})

        d1l = []
        for month in d1.keys():
            d1l.append(d1[month])

        # print(d1l)

        for i in range(len(months)):
            t = {}
            t['MeanUberTripDuration'] = d1l[i]
            t['MonthlyMaximumTemperature'] = l1s[i]['MonthlyMaximumTemperature']
            t['MonthlyTotalLiquidPrecipitation'] = l1s[i]['MonthlyTotalLiquidPrecipitation']
            t['MonthlyTotalSnowfall'] = l1s[i]['MonthlyTotalSnowfall']
            r[months[i]] = t

        # print(r)

        repo.dropCollection("reWeatherUber")
        repo.createCollection("reWeatherUber")
        repo['ctrinh.reWeatherUber'].insert_many([r])
        repo['ctrinh.reWeatherUber'].metadata({'complete':True})
        print(repo['ctrinh.reWeatherUber'].metadata())

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
        doc.add_namespace('dmc', 'http://datamechanics.io/data/')

        this_script = doc.agent('alg:ctrinh#reWeatherUber', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        # resource = doc.entity('dbg:datastore_search', {'prov:label':'Park Boston Monthly 2015', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        uber = doc.entity('dat:ctrinh#uber', {prov.model.PROV_LABEL:'Mean Car Travel Time', prov.model.PROV_TYPE:'ont:DataSet'})
        weather = doc.entity('dat:ctrinh#weather18', {prov.model.PROV_LABEL:'Weather 2015', prov.model.PROV_TYPE:'ont:DataSet'})
        get_reWeatherUber = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_reWeatherUber, this_script)
        doc.usage(get_reWeatherUber, uber, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'}
                  )
        doc.usage(get_reWeatherUber, weather, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'}
                  )

        reWeatherUber = doc.entity('dat:ctrinh#reWeatherUber', {prov.model.PROV_LABEL:'Monthly Weather and Total Uber Trip Duration', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(reWeatherUber, this_script)
        doc.wasGeneratedBy(reWeatherUber, get_reWeatherUber, endTime)
        doc.wasDerivedFrom(reWeatherUber, uber, get_reWeatherUber, get_reWeatherUber, get_reWeatherUber)
        doc.wasDerivedFrom(reWeatherUber, weather, get_reWeatherUber, get_reWeatherUber, get_reWeatherUber)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
reWeatherUber.execute()
doc = reWeatherUber.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof

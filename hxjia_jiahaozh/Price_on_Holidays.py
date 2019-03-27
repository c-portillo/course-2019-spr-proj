import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class Price_on_Holidays(dml.Algorithm):
    contributor = 'hxjia_jiahaozh'
    reads = ['hxjia_jiahaozh.US_Holidays', 'hxjia_jiahaozh.calendar']
    writes = ['hxjia_jiahaozh.Price_on_Holidays']

    @staticmethod
    def execute(trial=False):

        def project(R, p):
            return [p(t) for t in R]

        def select(R, s):
            return [t for t in R if s(t)]

        def product(R, S):
            return [(t, u) for t in R for u in S]

        def aggregate(R, f):
            keys = {r[0] for r in R}
            return [(key, f([v for (k, v) in R if k == key])) for key in keys]

        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')

        collection_holidays = repo.hxjia_jiahaozh.US_Holidays
        holidays = collection_holidays.find({})
        collection_calendar = repo.hxjia_jiahaozh.calendar
        calendar = collection_calendar.find({})

        holidays_data = []
        calendar_data = []
        for data in calendar:
            if data['price'] != 'null' and data['price'] is not None:
                calendar_data.append(data)
#       print(calendar_data)

#        print(calendar_data)
        calendar_data = project(calendar_data, lambda t: [t['date'], t['price'].replace("$", "").replace(",", "")])
        for i in calendar_data:
            i[1] = float(i[1])
        calendar_data = aggregate(calendar_data, lambda t: sum(t)/len(t))
#        print(calendar_data)
        for h in holidays:
            for t in calendar_data:
                if t[0] == h['Date']:
                    holidays_data.append((h['Date'], h['Holiday']))

        result_withH = product(calendar_data, holidays_data)
#        print(result_withH)
        result_withH = select(result_withH, lambda t: t[0][0] == t[1][0])

        result_withH = project(result_withH, lambda t: (t[0][0], t[0][1], t[1][1]))

        holidays_date = []
        for hd in holidays_data:
            holidays_date.append(hd[0])

        result_withoutH = []
        for c in calendar_data:
            if c[0] not in holidays_date:
                 result_withoutH.append(c)

        result_withoutH = project(result_withoutH, lambda t: (t[0], t[1], 'normal'))

        result = result_withoutH + result_withH

        result = project(result, lambda t: {'date': t[0], 'avg_price': t[1], 'holiday': t[2]})

        # r = json.loads(new_bl.to_json(orient='records'))
        # s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("Price_on_Holidays")
        repo.createCollection("Price_on_Holidays")
        repo['hxjia_jiahaozh.Price_on_Holidays'].insert_many(result)
        repo['hxjia_jiahaozh.Price_on_Holidays'].metadata({'complete': True})
        print(repo['hxjia_jiahaozh.Price_on_Holidays'].metadata())

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
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/hxjia_jiahaozh/')

        this_script = doc.agent('alg:hxjia_jiahaozh#price_on_holidays',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource1 = doc.entity('bdp:Calendar',
                              {'prov:label': 'Calendar, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        resource2 = doc.entity('bdp:US_Holidays',
                              {'prov:label': 'US_Holidays, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        transformation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transformation, this_script)
        doc.usage(transformation, resource1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Transformation',
                   'ont:Query': '?type=calendar&$select=date, price'
                   }
                  )
        doc.usage(transformation, resource2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Transformation',
                   'ont:Query': '?type=holidays&$select=date, holiday'
                   }
                  )

        priceonholidays = doc.entity('dat:hxjia_jiahaozh#price_on_holidays',
                          {prov.model.PROV_LABEL: 'Price on Holidays', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(priceonholidays, this_script)
        doc.wasGeneratedBy(priceonholidays, transformation, endTime)
        doc.wasDerivedFrom(priceonholidays, resource1, transformation, transformation, transformation)
        doc.wasDerivedFrom(priceonholidays, resource2, transformation, transformation, transformation)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Price_on_Holidays.execute()
# doc = Boston_Landmarks.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof

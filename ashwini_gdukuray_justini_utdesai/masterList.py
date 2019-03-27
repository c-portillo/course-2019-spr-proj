import json
import dml
import prov.model
import datetime
import pandas as pd
import uuid


class masterList(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = ['ashwini_gdukuray_justini_utdesai.massHousing', 'ashwini_gdukuray_justini_utdesai.secretary', 'ashwini_gdukuray_justini_utdesai.validZipCodes'] # is going to have to read in the master list from mongodb
    writes = ['ashwini_gdukuray_justini_utdesai.masterList'] # will write a dataset that is companies in top 25 that are also certified MBE

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        # Need to standardize the columns and field structure of massHousing and secretary and union the two
        # in order to create a master MBE list, and then store it in the DB

        massHousing = repo['ashwini_gdukuray_justini_utdesai.massHousing']
        secretary = repo['ashwini_gdukuray_justini_utdesai.secretary']
        validZips = repo['ashwini_gdukuray_justini_utdesai.validZipCodes']


        massHousingDF = pd.DataFrame(list(massHousing.find()))
        secretaryDF = pd.DataFrame(list(secretary.find()))
        validZipsDF = pd.DataFrame(list(validZips.find()))

        # clean up secretary dataset
        # convert zip codes to strings and 5 digits long
        secretaryDF['Zip'] = secretaryDF['Zip'].astype('str')
        secretaryDF['Zip'] = secretaryDF['Zip'].apply(lambda zipCode: ((5 - len(zipCode))*'0' + zipCode \
                                                        if len(zipCode) < 5 else zipCode)[:5])
        secretaryDF = secretaryDF.loc[secretaryDF['MBE - Y/N'] == 'Y']
        secretaryDF = secretaryDF[['Business Name', 'Address', 'City', 'Zip', 'State', 'Description of Services']]

        # create a more uniform ID
        businessIDs = []
        for index, row in secretaryDF.iterrows():
            busName = row['Business Name']
            cleanedText = busName.upper().strip().replace(' ','').replace('.','').replace(',','').replace('-','')
            businessIDs.append(cleanedText)

        secretaryDF['B_ID'] = pd.Series(businessIDs, index=secretaryDF.index)


        # clean up massHousing dataset
        massHousingDF['Zip'] = massHousingDF['Zip'].apply(lambda zipCode: zipCode[:5])
        massHousingDF = massHousingDF[['Business Name', 'Address', 'City', 'Zip', 'State', 'Primary Trade', 'Primary Other/Consulting Description']]

        businessIDs = []
        for index, row in massHousingDF.iterrows():
            busName = row['Business Name']
            cleanedText = busName.upper().strip().replace(' ','').replace('.','').replace(',','').replace('-','')
            businessIDs.append(cleanedText)

            if (row['Primary Trade'] == 'Other: Specify'):
                row['Primary Trade'] = row['Primary Other/Consulting Description']

        massHousingDF['B_ID'] = pd.Series(businessIDs, index=massHousingDF.index)

        massHousingDF = massHousingDF.rename(index=str, columns={'Primary Trade': 'Description of Services'})
        massHousingDF = massHousingDF.drop(columns=['Primary Other/Consulting Description'])


        # merge and create masterList
        preMasterList = pd.merge(massHousingDF, secretaryDF, how='outer', on=['B_ID', 'City', 'Zip'])

        preDict = {'B_ID': [], 'Business Name': [], 'Address': [], 'City': [], 'Zip': [], 'State': [], 'Description of Services': []}

        for index, row in preMasterList.iterrows():

            desc = row['Description of Services_x']

            preDict['B_ID'].append(row['B_ID'])
            preDict['City'].append(row['City'])
            preDict['Zip'].append(row['Zip'])

            if pd.isnull(desc):
                preDict['Business Name'].append(row['Business Name_y'])
                preDict['State'].append(row['State_y'])
                preDict['Address'].append(row['Address_y'])
                preDict['Description of Services'].append(row['Description of Services_y'])
            else:
                preDict['Business Name'].append(row['Business Name_x'])
                preDict['State'].append(row['State_x'])
                preDict['Address'].append(row['Address_x'])
                preDict['Description of Services'].append(row['Description of Services_x'])


        masterList = pd.DataFrame(preDict)

        # filter out invalid zips
        validZipsDF['Zip'] = validZipsDF['Zip'].astype('str')
        validZipsDF['Zip'] = validZipsDF['Zip'].apply(lambda zipCode: ((5 - len(zipCode))*'0' + zipCode \
                                                        if len(zipCode) < 5 else zipCode)[:5])
        listOfGoodZips = validZipsDF['Zip'].tolist()

        masterList = masterList[masterList['Zip'].isin(listOfGoodZips)]

        #records = json.loads(masterList.T.to_json()).values()

        #print(masterList)

        repo.dropCollection('masterList')
        repo.createCollection('masterList')
        repo['ashwini_gdukuray_justini_utdesai.masterList'].insert_many(masterList.to_dict('records'))
        repo['ashwini_gdukuray_justini_utdesai.masterList'].metadata({'complete': True})
        print(repo['ashwini_gdukuray_justini_utdesai.masterList'].metadata())

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

# 'ashwini_gdukuray_justini_utdesai.massHousing', 'ashwini_gdukuray_justini_utdesai.secretary', 'ashwini_gdukuray_justini_utdesai.validZipCodes'

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        #doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        selectProject = doc.agent('alg:ashwini_gdukuray_justini_utdesai#Selection&Projection',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        join = doc.agent('alg:ashwini_gdukuray_justini_utdesai#Join',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        massHousingDataPre = doc.entity('dat:ashwini_gdukuray_justini_utdesai#massHousingDataPre',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})
        secretaryCommonwealthDataPre = doc.entity('dat:ashwini_gdukuray_justini_utdesai#secretaryCommonwealthDataPre',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})
        validZipCodesData = doc.entity('dat:ashwini_gdukuray_justini_utdesai#validZipCodes',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})
        massHousingDataPost = doc.entity('dat:ashwini_gdukuray_justini_utdesai#MassHousingPost',
                                      {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                                       'ont:Extension': 'json'})
        secretaryCommonwealthDataPost = doc.entity('dat:ashwini_gdukuray_justini_utdesai#secretaryCommonwealthPost',
                                      {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                                       'ont:Extension': 'json'})
        preMasterList = doc.entity('dat:ashwini_gdukuray_justini_utdesai#preMasterList',
                                      {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                                       'ont:Extension': 'json'})
        MasterList =  doc.entity('dat:ashwini_gdukuray_justini_utdesai#MasterList',
                                      {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                                       'ont:Extension': 'json'})

        massHouse_act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        sec_act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        merge_act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        master_act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(massHouse_act, selectProject)
        doc.wasAssociatedWith(merge_act, join)
        doc.wasAssociatedWith(master_act, selectProject)

        doc.usage(massHouse_act, massHousingDataPre, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Query'})
        doc.usage(sec_act, secretaryCommonwealthDataPre, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Query'})
        doc.usage(merge_act, massHousingDataPost, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Query'})
        doc.usage(merge_act, secretaryCommonwealthDataPost, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Query'})
        doc.usage(master_act, preMasterList, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Query'})
        doc.usage(master_act, validZipCodesData, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Query'})

        doc.wasAttributedTo(massHousingDataPre, selectProject)
        doc.wasAttributedTo(secretaryCommonwealthDataPre, selectProject)
        doc.wasAttributedTo(massHousingDataPost, join)
        doc.wasAttributedTo(secretaryCommonwealthDataPost, join)
        doc.wasAttributedTo(preMasterList, selectProject)
        doc.wasAttributedTo(validZipCodesData, selectProject)

        doc.wasGeneratedBy(massHousingDataPost, massHouse_act, endTime)
        doc.wasGeneratedBy(secretaryCommonwealthDataPost, sec_act, endTime)
        doc.wasGeneratedBy(preMasterList, merge_act, endTime)
        doc.wasGeneratedBy(MasterList, master_act, endTime)

        doc.wasDerivedFrom(massHousingDataPost, massHousingDataPre, massHouse_act, massHouse_act, massHouse_act)
        doc.wasDerivedFrom(secretaryCommonwealthDataPost, secretaryCommonwealthDataPre, sec_act, sec_act, sec_act)
        doc.wasDerivedFrom(preMasterList, massHousingDataPost, merge_act, merge_act, merge_act)
        doc.wasDerivedFrom(preMasterList, secretaryCommonwealthDataPost, merge_act, merge_act, merge_act)
        doc.wasDerivedFrom(MasterList, preMasterList, master_act, master_act, master_act)
        doc.wasDerivedFrom(MasterList, validZipCodesData, master_act, master_act, master_act)


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

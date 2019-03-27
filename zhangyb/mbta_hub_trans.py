import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class mbta_hub_trans(dml.Algorithm):
    contributor = 'zhangyb'
    reads = ['zhangyb.mbta_station',
             'zhangyb.hub_station']
    writes = ['zhangyb.mbta_hub']

    @staticmethod
    def execute(trial = False):

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zhangyb', 'zhangyb')

        repo.dropPermanent("mbta_hub")
        repo.createPermanent("mbta_hub")

        # Retrieve data from MongoDB
        mbta = repo['zhangyb.mbta_station']
        hub = repo['zhangyb.hub_station']

        mbta_json = mbta.find()
        hub_json = hub.find()

        '''
        Tranformation 1:
        Aggregate data based on Locations
        Both Mbta and Hubway datasets have the attributes: Longitudes and Latitudes
        New dataset will have attributes: ID, Type(MBTA or Hubway), Latitudes, Longitudes
        The combined new dataset can be helpful to find areas with poor transportations
        '''

        data = {'Data': []}
        count = 0

        for obj in mbta_json:
            count = len(obj['data'])
            for i in range(count):
                data['Data'] += [{'ID': i,'Type': 'MBTA', 'Latitudes':obj['data'][i]['attributes']['latitude'], 'Longitudes':obj['data'][i]['attributes']['longitude']}]

        for obj in hub_json:
            for i in range(len(obj['objects'])):
                data['Data'] += [{'ID': i + count,'Type': 'Hubway', 'Latitudes':obj['objects'][i]['point']['coordinates'][1], 'Longitudes':obj['objects'][i]['point']['coordinates'][0]}]

        repo['zhangyb.mbta_hub'].insert_one(data)
        repo['zhangyb.mbta_hub'].metadata({'complete':True})

        #repo.logout()

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
        repo.authenticate('zhangyb', 'zhangyb')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format. 
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format. 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:zhangyb#MbtaHubway_Trans',{prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        get_mbta_hub = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_mbta_hub, this_script)

        mbta = doc.entity('dat:zhangyb#mbta_station', {prov.model.PROV_LABEL:'MBTA Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(get_mbta_hub, mbta, startTime)

        hub = doc.entity('dat:zhangyb#hub_station', {prov.model.PROV_LABEL:'Hubway Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(get_mbta_hub, hub, startTime)

        mbta_hub = doc.entity('dat:zhangyb#mbta_hub', {'prov:label':'MBTA and Hubway Stations', prov.model.PROV_TYPE:'ont:Dataset'})

        doc.wasAttributedTo(mbta_hub, this_script)
        doc.wasGeneratedBy(mbta_hub, get_mbta_hub, endTime)
        doc.wasDerivedFrom(mbta_hub, mbta, get_mbta_hub, get_mbta_hub, get_mbta_hub)
        doc.wasDerivedFrom(mbta_hub, hub, get_mbta_hub, get_mbta_hub, get_mbta_hub)

        #repo.logout()

        return doc

'''
MbtaHubway_Trans.execute()
doc = MbtaHubway_Trans.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''


        

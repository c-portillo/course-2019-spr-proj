import requests
import json
import dml
import prov.model
import datetime
import uuid
from bs4 import BeautifulSoup as bs

class famous_people(dml.Algorithm):
    contributor = 'mmao95_Dongyihe_weijiang_zhukk'
    reads = []
    writes = [contributor + '.famous_people']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        writes = [contributor + '.famous_people']
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        doc = requests.get("https://www.50states.com/bio/mass.htm").text
        soup = bs(doc, features='lxml')
        names = [e.text for e in soup.select("#content b")]
        list = []
        for name in names:
            parts = name.split()
            obj = {
                'full_name': name,
                'first_name': parts[0],
                'last_name': parts[-1] if len(parts) > 1 else None,
                'middle_name': parts[1:-1] if len(parts) > 2 else None
            }
            list.append(obj)

        repo.dropCollection('famous_people')
        repo.createCollection('famous_people')
        repo[writes[0]].insert_many(list)

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

        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://www.50states.com/bio/mass.htm')

        this_script = doc.agent('alg:'+contributor+'#famous_people', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_names = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_names, this_script)
        doc.usage(get_names, resource, startTime, None,
            {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Computation':'Data cleaning'
            }
        )

        fp = doc.entity('dat:'+contributor+'#famous_people', {prov.model.PROV_LABEL:'Famous People', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(fp, this_script)
        doc.wasGeneratedBy(fp, get_names, endTime)
        doc.wasDerivedFrom(fp, resource, get_names, get_names, get_names)

        repo.logout()
                  
        return doc

## eof
import json
import dml
import prov.model
import datetime
import uuid
import itertools

class filtered_famous_people_streets(dml.Algorithm):
    contributor = 'mmao95_Dongyihe_weijiang_zhukk'
    reads = [contributor + '.famous_people', contributor + '.street_book']
    writes = [contributor + '.filtered_famous_people_streets']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        contributor = 'mmao95_Dongyihe_weijiang_zhukk'
        reads = [contributor + '.famous_people', contributor + '.street_book']
        writes = [contributor + '.filtered_famous_people_streets']
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(contributor, contributor)

        famous_people = repo[reads[0]].find()
        street_book = repo[reads[1]].find()
        fp = set(itertools.chain(*{(n['first_name'], n['last_name']) for n in famous_people}))
        sb = [t for t in street_book if t['Street Name'] not in fp]
        repo.dropCollection('filtered_famous_people_streets')
        repo.createCollection('filtered_famous_people_streets')
        repo[writes[0]].insert_many(sb)

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

        this_script = doc.agent('alg:'+contributor+'#filtered_famous_people_streets', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        res_fp = doc.entity('bdp:fp', {'prov:label':'Famous People in MA', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        res_sb = doc.entity('bdp:sb', {'prov:label':'Street Book', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        filter_names = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(filter_names, this_script)
        doc.usage(filter_names, res_fp, startTime, None,
            {prov.model.PROV_TYPE: 'ont:Computation',
            'ont:Computation':'Selection, Differentiate'
            }
        )
        doc.usage(filter_names, res_sb, startTime, None,
            {prov.model.PROV_TYPE: 'ont:Computation',
            'ont:Computation':'Selection, Differentiate'
            }
        )
        result = doc.entity('dat:'+contributor+'#filtered_famous_people_streets', {prov.model.PROV_LABEL:'Streets without Famous People', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(result, this_script)
        doc.wasGeneratedBy(result, filter_names, endTime)
        doc.wasDerivedFrom(result, res_fp, filter_names, filter_names, filter_names)
        doc.wasDerivedFrom(result, res_sb, filter_names, filter_names, filter_names)
        repo.logout()
                  
        return doc

## eof
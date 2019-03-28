import dml
import prov.model
import datetime
import uuid
import aheckman_jfimbres.Helpers.transformations as t

list_of_states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
  "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
  "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
  "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
  "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
  "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
  "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
  "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

class emissions_per_capita(dml.Algorithm):
    contributor = 'aheckman_jfimbres'
    reads = ['aheckman_jfimbres.carbon_efficacy', 'aheckman_jfimbres.census']
    writes = ['aheckman_jfimbres.emissions_per_capita']
    @staticmethod
    def execute(trial = False):
        '''Give the adjusted emissions per capita on a state-by-state basis'''
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')

        co2_adjusted = repo.aheckman_jfimbres.co2_adjusted.find({})
        c = repo.aheckman_jfimbres.census.find({})

        adj = t.project(t.select(co2_adjusted, lambda x: x['State'] in list_of_states), lambda x: (x['State'], x['2016']*1000000))
        pops = t.project(t.select(c, lambda x: x['NAME'] in list_of_states), lambda x: (x['NAME'], x['POPESTIMATE2017']))
        # adj is given in x millions, so it needs to be scaled up to match population, which is just given in x

        tons = t.aggregate(t.union(adj, pops), lambda vs: (vs[0]/vs[1]))
        epc = dict(t.project(tons, lambda t: (t[0], str(t[1])+" Metric Tons per person")))

        repo.dropCollection("emissions_per_capita")
        repo.createCollection("emissions_per_capita")
        repo["aheckman_jfimbres.emissions_per_capita"].insert(epc)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:aheckman_jfimbres#emissions_per_capita',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        find_epc = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        co2_adjusted = doc.entity('dat:aheckman_jfimbres#co2_adjusted', {prov.model.PROV_LABEL:'Adjusted Carbon Emissions', prov.model.PROV_TYPE:'ont:DataSet'})
        census = doc.entity('dat:aheckman_jfimbres#census', {prov.model.PROV_LABEL:'Census Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAssociatedWith(find_epc, this_script)

        doc.usage(find_epc, co2_adjusted, startTime, None)
        doc.usage(find_epc, census, startTime, None)

        emissions_per_capita = doc.entity('dat:aheckman_jfimbres#emissions_per_capita', {prov.model.PROV_LABEL:'Emissions Per Capita', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(emissions_per_capita, this_script)
        doc.wasGeneratedBy(emissions_per_capita, find_epc, endTime)
        doc.wasDerivedFrom(emissions_per_capita, co2_adjusted, find_epc)
        doc.wasDerivedFrom(emissions_per_capita, census, find_epc)

        return doc

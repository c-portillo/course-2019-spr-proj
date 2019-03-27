import numpy as np
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

class carbon_efficacy(dml.Algorithm):
    contributor = 'aheckman_jfimbres'
    reads = ['aheckman_jfimbres.co2_adjusted', 'aheckman_jfimbres.co2_unadjusted', 'aheckman_jfimbres.carbon_intesity']
    writes = ['aheckman_jfimbres.carbon_efficacy']
    @staticmethod
    def execute(trial = False):
        '''Find the efficiency of carbon usage on a stat-by-state basis'''
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')

        co2_adjusted = repo.aheckman_jfimbres.co2_adjusted.find({})
        co2_unadjusted = repo.aheckman_jfimbres.co2_unadjusted.find({})
        carbon_intensity = repo.aheckman_jfimbres.carbon_intensity.find({})

        adj = t.project(t.select(co2_adjusted, lambda x: x['State'] in list_of_states), lambda x: (x['State'], x['2016']))
        unadj = t.project(t.select(co2_unadjusted, lambda x: x['State'] in list_of_states), lambda x: (x['State'], x['Total']))
        intense = t.project(t.select(carbon_intensity, lambda x: x['State'] in list_of_states), lambda x: (x['State'], x['2016']))

        emissions = t.aggregate(t.union(adj, unadj), np.mean)
        efficacy = dict(t.aggregate(t.union(emissions, intense), lambda v: [(v[0]/v[1])]))
        repo.dropCollection("carbon_efficacy")
        repo.createCollection("carbon_efficacy")
        repo['aheckman_jfimbres.carbon_efficacy'].insert(efficacy)

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

        this_script = doc.agent('alg:aheckman_jfimbres#carbon_efficacy',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        find_efficacy = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        co2_adjusted = doc.entity('dat:aheckman_jfimbres#co2_adjusted', {prov.model.PROV_LABEL:'Adjusted Carbon Emissions', prov.model.PROV_TYPE:'ont:DataSet'})
        co2_unadjusted = doc.entity('dat:aheckman_jfimbres#co2_unadjusted', {prov.model.PROV_LABEL:'Unadjusted Carbon Emissions', prov.model.PROV_TYPE:'ont:DataSet'})
        carbon_intensity = doc.entity('dat:aheckman_jfimbres#carbon_intensity', {prov.model.PROV_LABEL:'Carbon Intensity', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAssociatedWith(find_efficacy, this_script)

        doc.usage(find_efficacy, co2_adjusted, startTime, None)
        doc.usage(find_efficacy, co2_unadjusted, startTime, None)
        doc.usage(find_efficacy, carbon_intensity, startTime, None)

        efficacy = doc.entity('dat:aheckman_jfimbres#carbon_efficacy', {prov.model.PROV_LABEL:'Carbon Efficacy', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(efficacy, this_script)
        doc.wasGeneratedBy(efficacy, find_efficacy, endTime)
        doc.wasDerivedFrom(efficacy, co2_adjusted, find_efficacy)
        doc.wasDerivedFrom(efficacy, co2_unadjusted, find_efficacy)
        doc.wasDerivedFrom(efficacy, carbon_intensity, find_efficacy)

        return doc

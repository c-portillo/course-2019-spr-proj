import dml
import prov.model
import datetime
import uuid
import aheckman_jfimbres.Helpers.transformations as t

class opinion_vs_efficacy(dml.Algorithm):
    contributor = 'aheckman_jfimbres'
    reads = ['aheckman_jfimbres.carbon_efficacy', 'aheckman_jfimbres.partisan_map']
    writes = ['aheckman_jfimbres.opinion_by_efficacy']
    @staticmethod
    def execute(trial = False):
        '''Return data that shows carbon efficacy alongside partisan climate opinion data'''
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')

        efficacy = repo.aheckman_jfimbres.carbon_efficacy.find({})
        opinions = repo.aheckman_jfimbres.partisan_map.find({})

        state_ops = t.select(opinions, lambda x: x['GeoType'] == 'State')
        ops_by_state = t.project(state_ops, lambda x: [x['GeoName'], x['Group'], x['congress'], x['congressOppose'],
                                                       x['corporations'], x['corporationsOppose'], x['citizens'],  x['citizensOppose'],
                                                       x['regulate'], x['regulateOppose'], x['exp'], x['expOppose'],
                                                       x['prienv'], x['prienvOppose'], x['happening'], x['happeningOppose'],
                                                       x['human'], x['humanOppose'], x['consensus'], x['consensusOppose'],
                                                       x['worried'], x['worriedOppose'], x['harmUS'], x['harmUSOppose']])
        eff = t.project(efficacy, lambda x: x)
        ops_w_eff = dict(t.project(ops_by_state, lambda x: [x[0], (eff[0][x[0]], x[1:])]))

        repo.dropCollection("opinion_by_efficacy")
        repo.createCollection("opinion_by_efficacy")
        repo['aheckman_jfimbres.opinion_by_efficacy'].insert(ops_w_eff)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:aheckman_jfimbres#opinion_vs_efficacy',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        combine_op_eff = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        carbon_efficacy = doc.entity('dat:aheckman_jfimbres#carbon_efficacy',
                                  {prov.model.PROV_LABEL: 'Carbon Efficacy',
                                   prov.model.PROV_TYPE: 'ont:DataSet'})
        partisan_map = doc.entity('dat:aheckman_jfimbres#partisan_map',
                            {prov.model.PROV_LABEL: 'Responses to questions on climate change ordered by party affiliation',
                             prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAssociatedWith(combine_op_eff, this_script)

        doc.usage(combine_op_eff, carbon_efficacy, startTime, None)
        doc.usage(combine_op_eff, partisan_map, startTime, None)

        opinion_by_efficacy = doc.entity('dat:aheckman_jfimbres#opinion_by_efficacy',
                                          {prov.model.PROV_LABEL: 'Responses to important questions with state efficacy',
                                           prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(opinion_by_efficacy, this_script)
        doc.wasGeneratedBy(opinion_by_efficacy, combine_op_eff, endTime)
        doc.wasDerivedFrom(opinion_by_efficacy, carbon_efficacy, combine_op_eff)
        doc.wasDerivedFrom(opinion_by_efficacy, partisan_map, combine_op_eff)

        return doc
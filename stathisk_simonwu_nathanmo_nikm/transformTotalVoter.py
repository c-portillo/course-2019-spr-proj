import prov.model
import dml
import datetime
import uuid
import json
# from stathisk_simonwu_nathanmo_nikm.builtin import project

class transformTotalVoter(dml.Algorithm):
    contributor = 'stathisk_simonwu_nathanmo_nikm'
    reads = ['stathisk_simonwu_nathanmo_nikm.democratic_primary', 'stathisk_simonwu_nathanmo_nikm.republican_primary', 'stathisk_simonwu_nathanmo_nikm.greenrainbow_primary',
             'stathisk_simonwu_nathanmo_nikm.mapping']
    # writes = ['stathisk_simonwu_nathanmo_nikm.three_parties_blanksandvotes_c_w_p',
    writes = ['stathisk_simonwu_nathanmo_nikm.democratic_county_vote_stat',
              'stathisk_simonwu_nathanmo_nikm.republican_county_vote_stat',
              'stathisk_simonwu_nathanmo_nikm.greenrainbow_county_vote_stat']

    @staticmethod
    def aggregate(R, f):
        keys = {r[0] for r in R}
        return [(key, f([v for (k, v) in R if k == key])) for key in keys]

    @staticmethod
    def select(R, s):
        return [t for t in R if s(t)]

    @staticmethod
    def project(R, p):
        return [p(t) for t in R]

    @staticmethod
    def product(R, S):
        return [(t, u) for t in R for u in S]


    @staticmethod
    def findmapping(records):
        m = {}
        dirs = ['North', 'West', 'South', 'East']
        for r in records:
            cityname = r['city']
            for d in dirs:
                if d in cityname:
                    spot = cityname.replace(d, '').strip()
                    m[spot] = r['county_name']


            m[r['city']] = r['county_name']

        return m

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')

        democratic = repo['stathisk_simonwu_nathanmo_nikm.democratic_primary'].find()
        republican = repo['stathisk_simonwu_nathanmo_nikm.republican_primary'].find()
        greenrainbow = repo['stathisk_simonwu_nathanmo_nikm.greenrainbow_primary'].find()
        mapping = repo['stathisk_simonwu_nathanmo_nikm.mapping'].find()

        if trial:
            democratic = democratic[1:10]
            republican = republican[1:10]
            greenrainbow = greenrainbow[1:10]

        # project data to form (City/Town, Ward, Pct, Blanks, Total Votes Cast)
        projection_rules = lambda x: {'City/Town': x['City/Town'],
                                      'Ward': x['Ward'],
                                      'Pct': x['Pct'],
                                      'Blanks': x['Blanks'],
                                      'Total Votes Cast': x['Total Votes Cast']}
        uniform_democratic = transformTotalVoter.project(democratic, projection_rules)
        uniform_republican = transformTotalVoter.project(republican, projection_rules)
        uniform_greenrainbow = transformTotalVoter.project(greenrainbow, projection_rules)

        def choose_key(record):
            first, second = record[0], record[1]
            # if City/Town, ward, Pct all equals to another ones
            return first['City/Town'] == second['City/Town'] \
                   and first['Ward'] == second['Ward'] \
                   and first['Pct'] == second['Pct']

        all_conbine = transformTotalVoter.product(uniform_democratic, uniform_republican)
        conbine_with_key = transformTotalVoter.select(all_conbine, choose_key)
        rearrange = lambda x : {'City/Town': x[0]['City/Town'],
                                   'Ward': x[0]['Ward'],
                                   'Pct': x[0]['Pct'],
                                   'Blanks democratic': x[0]['Blanks'],
                                   'Total Votes Cast democratic': x[0]['Total Votes Cast'],
                                   'Blanks republican': x[1]['Blanks'],
                                   'Total Votes Cast republican': x[1]['Total Votes Cast']}

        # {City/Town, Ward, Pct, Blank party 1, Total votes party 1, Blank party 2, Total votes party 2}
        projection_with_two = transformTotalVoter.project(conbine_with_key, rearrange)

        all_conbine_three = transformTotalVoter.product(projection_with_two, uniform_greenrainbow)
        conbine_with_key = transformTotalVoter.select(all_conbine_three, choose_key)

        rearrange = lambda x: {'City/Town': x[0]['City/Town'],
                                  'Ward': x[0]['Ward'],
                                  'Pct': x[0]['Pct'],
                                  'Blanks democratic': x[0]['Blanks democratic'],
                                  'Total Votes Cast democratic': x[0]['Total Votes Cast democratic'],
                                  'Blanks republican': x[0]['Blanks republican'],
                                  'Total Votes Cast republican': x[0]['Total Votes Cast republican'],
                                  'Blanks greenrainbow': x[1]['Blanks'],
                                  'Total Votes Cast greenrainbow': x[1]['Total Votes Cast']}


        " data form: C/T, W, P, Blanks & Total votes for 3 parties "
        projection_with_three = transformTotalVoter.project(conbine_with_key, rearrange)
        # repo.dropCollection('three_parties_blanksandvotes_c_w_p')
        # repo.createCollection('three_parties_blanksandvotes_c_w_p')
        # repo['stathisk_simonwu_nathanmo_nikm.three_parties_blanksandvotes_c_w_p'].insert_many(projection_with_three)
        # repo['stathisk_simonwu_nathanmo_nikm.three_parties_blanksandvotes_c_w_p'].metadata({'complete': True})

        " { city_name : county }"
        city_county_map = transformTotalVoter.findmapping(mapping)

        def replace_key_with_county(dataest, mark):
            res, f = None, None
            if mark == 'd':
                f = lambda x: (city_county_map[x['City/Town']] if x['City/Town'] in city_county_map else x['City/Town'],
                               int(x['Total Votes Cast democratic'].replace(',', '')))
            elif mark == 'r':
                f = lambda x: (city_county_map[x['City/Town']] if x['City/Town'] in city_county_map else x['City/Town'],
                               int(x['Total Votes Cast republican'].replace(',', '')))
            elif mark == 'g':
                f = lambda x: (city_county_map[x['City/Town']] if x['City/Town'] in city_county_map else x['City/Town'],
                               int(x['Total Votes Cast greenrainbow'].replace(',', '')))
            res = transformTotalVoter.project(dataest, f)
            return res

        county_democratic = replace_key_with_county(projection_with_three, 'd')
        county_republican = replace_key_with_county(projection_with_three, 'r')
        county_greenrainbow = replace_key_with_county(projection_with_three, 'g')

        county_democratic_aggr_sum = transformTotalVoter.aggregate(county_democratic, sum)
        county_republican_aggr_sum = transformTotalVoter.aggregate(county_republican, sum)
        county_greenrainbow_aggr_sum = transformTotalVoter.aggregate(county_greenrainbow, sum)

        out_file1 = transformTotalVoter.project(county_democratic_aggr_sum,
                                    lambda x: {'County': x[0],
                                               'Total Votes Cast': x[1]})
        out_file2 = transformTotalVoter.project(county_republican_aggr_sum,
                                    lambda x: {'County': x[0],
                                               'Total Votes Cast': x[1]})
        out_file3 = transformTotalVoter.project(county_greenrainbow_aggr_sum,
                                    lambda x: {'County': x[0],
                                               'Total Votes Cast': x[1]})

        repo.dropCollection('democratic_county_vote_stat')
        repo.createCollection('democratic_county_vote_stat')
        repo['stathisk_simonwu_nathanmo_nikm.democratic_county_vote_stat'].insert_many(json.loads(json.dumps(out_file1)))
        repo['stathisk_simonwu_nathanmo_nikm.democratic_county_vote_stat'].metadata({'complete': True})

        repo.dropCollection('republican_county_vote_stat')
        repo.createCollection('republican_county_vote_stat')
        repo['stathisk_simonwu_nathanmo_nikm.republican_county_vote_stat'].insert_many(json.loads(json.dumps(out_file2)))
        repo['stathisk_simonwu_nathanmo_nikm.republican_county_vote_stat'].metadata({'complete': True})

        repo.dropCollection('greenrainbow_county_vote_stat')
        repo.createCollection('greenrainbow_county_vote_stat')
        repo['stathisk_simonwu_nathanmo_nikm.greenrainbow_county_vote_stat'].insert_many(json.loads(json.dumps(out_file3)))
        repo['stathisk_simonwu_nathanmo_nikm.greenrainbow_county_vote_stat'].metadata({'complete': True})

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('stathisk_simonwu_nathanmo_nikm', 'stathisk_simonwu_nathanmo_nikm')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:stathisk_simonwu_nathanmo_nikm#transformTotalVoter',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        dp = doc.entity('dat:democratic_primary',
                              {'prov:label': 'democratic_primary data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        rp = doc.entity('dat:republican_primary',
                        {'prov:label': 'republican_primary data', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})
        gp = doc.entity('dat:greenrainbow_primary',
                        {'prov:label': 'greenrainbow_primary data', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})
        mapping_rough = doc.entity('dat:mapping',
                        {'prov:label': 'mapping data', prov.model.PROV_TYPE: 'ont:DataResource',
                         'ont:Extension': 'json'})

        get_democratic_stat_bycounty = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_republican_stat_bycounty = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_greenrainbow_stat_bycounty = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_feaible_transform = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_democratic_stat_bycounty, this_script)
        doc.wasAssociatedWith(get_republican_stat_bycounty, this_script)
        doc.wasAssociatedWith(get_greenrainbow_stat_bycounty, this_script)
        doc.wasAssociatedWith(get_feaible_transform, this_script)

        doc.usage(get_democratic_stat_bycounty, dp, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:DataResource'})
        doc.usage(get_republican_stat_bycounty, rp, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:DataResource'})
        doc.usage(get_greenrainbow_stat_bycounty, gp, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:DataResource'})
        doc.usage(get_feaible_transform, mapping_rough, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:DataResource'})

        democratic_vote_stat_by_county = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#democratic_county_vote_stat',
                                {prov.model.PROV_LABEL: 'democratic vote stat by county', prov.model.PROV_TYPE: 'ont:DataSet'})
        republican_vote_stat_by_county = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#republican_county_vote_stat',
                                {prov.model.PROV_LABEL: 'republican vote stat by county', prov.model.PROV_TYPE: 'ont:DataSet'})
        greenrainbow_vote_stat_by_county = doc.entity('dat:stathisk_simonwu_nathanmo_nikm#greenrainbow_county_vote_stat',
                                  {prov.model.PROV_LABEL: 'greenrainbow vote stat by county', prov.model.PROV_TYPE: 'ont:DataSet'})

        mapping_relation = doc.entity('dat:mapping relation',
                                  {prov.model.PROV_LABEL: 'city to county', prov.model.PROV_TYPE: 'ont:DataSet'})


        doc.wasAttributedTo(democratic_vote_stat_by_county, this_script)
        doc.wasAttributedTo(republican_vote_stat_by_county, this_script)
        doc.wasAttributedTo(greenrainbow_vote_stat_by_county, this_script)
        doc.wasAttributedTo(mapping_relation, this_script)

        doc.wasGeneratedBy(democratic_vote_stat_by_county, get_democratic_stat_bycounty, endTime)
        doc.wasGeneratedBy(republican_vote_stat_by_county, get_republican_stat_bycounty, endTime)
        doc.wasGeneratedBy(greenrainbow_vote_stat_by_county, get_greenrainbow_stat_bycounty, endTime)
        doc.wasGeneratedBy(mapping_relation, mapping_rough, endTime)

        doc.wasDerivedFrom(democratic_vote_stat_by_county, dp, get_democratic_stat_bycounty,
                           mapping_relation, get_democratic_stat_bycounty)
        doc.wasDerivedFrom(republican_vote_stat_by_county, rp, get_republican_stat_bycounty,
                           mapping_relation, get_republican_stat_bycounty)
        doc.wasDerivedFrom(greenrainbow_vote_stat_by_county, gp, get_greenrainbow_stat_bycounty,
                           mapping_relation, get_greenrainbow_stat_bycounty)

        repo.logout()
        return doc

if __name__ == '__main__':
    transformTotalVoter.execute(False)


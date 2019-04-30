import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import operator

class registered_voters_didnt_turn_out(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ['carlosp_jpva_tkay_yllescas.registered_by_ward', 'carlosp_jpva_tkay_yllescas.results_2017','carlosp_jpva_tkay_yllescas.city_race_diff_to_flip','carlosp_jpva_tkay_yllescas.sampling']
    writes = ['carlosp_jpva_tkay_yllescas.registered_voters_didnt_turn_out', 'carlosp_jpva_tkay_yllescas.wards_to_visit']

    @staticmethod
    def execute(flip_percentage_constraint, hispanic_proportion_constraint):
        print("registered_voters_didnt_turn_out")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        repo.dropCollection("registered_voters_didnt_turn_out")
        repo.createCollection("registered_voters_didnt_turn_out")

        repo.dropCollection("carlosp_jpva_tkay_yllescas.wards_to_visit")
        repo.createCollection("carlosp_jpva_tkay_yllescas.wards_to_visit")


        # Grab datasets from database
        registered = (repo['carlosp_jpva_tkay_yllescas.registered_by_ward']).find()
        results_2017 = (repo['carlosp_jpva_tkay_yllescas.results_2017']).find()
        demographics_db = (repo['carlosp_jpva_tkay_yllescas.sampling']).find()

        #get the keys 
        total_registered_by_ward = {}
        for ward in registered:
            total_registered = 0
            keys = ward.keys()
            for key in keys:
                if key != '_id':
                    total_registered_by_ward[key] = ward[key]['Total']
        total_ballots_cast_by_ward = {}            
        for ward in results_2017:
            print("test", ward)
            if ward['Candidate'] == 'VOTES CAST':
                keys = ward.keys()
                for key in keys:
                    if key != 'Candidate' and key != '_id':
                        total_ballots_cast_by_ward[key] = ward[key]
        
        total_who_didnt_turn_out_by_ward = {}
        print("keys",total_registered_by_ward.keys())
        total_registered_by_ward_keys = list(total_registered_by_ward.keys())
        total_ballots_cast_by_ward_keys = list(total_ballots_cast_by_ward.keys())

        for i in range(22):
            #print(total_registered_by_ward[total_registered_by_ward_keys[i]])
            #print(total_ballots_cast_by_ward[total_ballots_cast_by_ward_keys[i]])
            total_who_didnt_turn_out_by_ward[total_ballots_cast_by_ward_keys[i]] = int(total_registered_by_ward[total_registered_by_ward_keys[i]]) - int(total_ballots_cast_by_ward[total_ballots_cast_by_ward_keys[i]])

        

       # print("total registered by ward ", total_registered_by_ward)
        #print("------------------------------")
        #print("total_ballots_cast_by_ward", total_ballots_cast_by_ward)
        #print("final result: total people who were registered and didn't turn out", total_who_didnt_turn_out_by_ward)

        

        endTime = datetime.datetime.now()

        ##sort total who didnt turn out by ward
        sorted_total = sorted(total_who_didnt_turn_out_by_ward.items(), key=operator.itemgetter(1), reverse= True)


        print("sorted total", sorted_total)
        diff_to_flip = (repo['carlosp_jpva_tkay_yllescas.city_race_diff_to_flip']).find({},{"total_diff" : 1})
        for x in diff_to_flip:
            diff_to_flip = x['total_diff']
        print('diff_to_flip',diff_to_flip)
        hispanic_total = {}
        
        i = 1

        for ward in (repo['carlosp_jpva_tkay_yllescas.sampling']).find():
            keys = ward.keys()
            print("keys", keys)
            for key in keys:
                if key != '_id'  and key != 'aggregate':
                    #print("key",key)
                    hispanic_total[str(i)] = ward[key]['H_Prop']
                    i += 1
        #print("total" , hispanic_total)



        

        total_flipped = 0
       # flip_percentage_constraint = 0.5
       # hispanic_proportion_constraint = 0.04
        possible = False
        wards_to_visit = {}
        

        for ward, total in sorted_total:
            if (total_flipped >= diff_to_flip):
                possible = True
                break;
            projected_flip = int(total * flip_percentage_constraint)
           # print("hispanic proportion for ward" + str(ward) , hispanic_total[str(ward)] )
            if float(hispanic_total[ward]) > hispanic_proportion_constraint:
                total_flipped += projected_flip
                wards_to_visit[ward] = projected_flip
            #    print("     added")
           
            
            
            
     
       

            #do something if not possible?
        return json.dumps(wards_to_visit)




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
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', './carlosp_jpva_tkay_yllescas')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', './data')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#registered_voters_didnt_turn_out',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        registered_by_ward = doc.entity('dat:data#registered_by_ward',
                              {'prov:label': 'Eligible voters in all Precincts in MA', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        results_2017 = doc.entity('dat:data#results_2017',
                              {'prov:label': '2017 City election results', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_ward_total= doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_hispanic_population = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        constraint_solver  = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_ward_total, this_script)
        doc.wasAssociatedWith(get_hispanic_population, this_script)
        doc.wasAssociatedWith(constraint_solver, this_script)

        doc.usage(get_ward_total, results_2017, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(get_hispanic_population, registered_by_ward, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(constraint_solver, get_hispanic_population, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        voters_not_turnout = doc.entity('dat:/registered_voters_didnt_turn_out', {prov.model.PROV_LABEL: "Registered voters who didn't turn out ", prov.model.PROV_TYPE: 'ont:DataSet'})
        wards_to_visit = doc.entity('dat:/wards_to_visit', {prov.model.PROV_LABEL: 'Wards to visit that satisfy constraints', prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(voters_not_turnout, this_script)
        doc.wasGeneratedBy(voters_not_turnout, get_ward_total, endTime)
        doc.wasDerivedFrom(voters_not_turnout, results_2017, get_ward_total)

        doc.wasAttributedTo(wards_to_visit, this_script)
        doc.wasGeneratedBy(wards_to_visit, get_hispanic_population, endTime)
        doc.wasDerivedFrom(wards_to_visit, registered_by_ward, get_hispanic_population)

        repo.logout()

        return doc
#registered_voters_didnt_turn_out.execute()

## eof
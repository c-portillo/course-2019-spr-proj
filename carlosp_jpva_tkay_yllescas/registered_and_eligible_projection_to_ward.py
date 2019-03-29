import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class registered_and_eligible_projection_to_ward(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ['carlosp_jpva_tkay_yllescas.registered_precincts', 'carlosp_jpva_tkay_yllescas.non_registered_precincts']
    writes = ['carlosp_jpva_tkay_yllescas.registered_by_ward', 'carlosp_jpva_tkay_yllescas.eligible_by_ward']

    @staticmethod
    def execute(trial=False):
        print("registered_and_eligible_aggregation")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        repo.dropCollection("registered_by_ward")
        repo.createCollection("registered_by_ward")

        repo.dropCollection("eligible_by_ward")
        repo.createCollection("eligible_by_ward")

        # Grab datasets from database
        registered = (repo['carlosp_jpva_tkay_yllescas.registered_precincts']).find()
        eligible = (repo['carlosp_jpva_tkay_yllescas.non_registered_precincts']).find()

        # Filter out all cities that aren't Boston
        registered_boston_ward = []
        eligible_boston_ward = []
        for reg in registered: # Registered voters
            if "Boston" in reg["Precinct"]:
                location = reg["Precinct"].split()
                if len(location) == 3:
                    reg["Precinct"] = location[2]
                    reg["Ward"] = location[1]
                    registered_boston_ward.append(reg)
        for elig in eligible: # Eligible/Non-registered voters
            if "Boston" in elig["Precinct"]:
                location = elig["Precinct"].split()
                if len(location) == 3:
                    elig["Precinct"] = location[2]
                    elig["Ward"] = location[1]
                    eligible_boston_ward.append(elig)

        # Create a set of all the wards in Boston for both sets of data
        rkeys = {x["Ward"]:{} for x in registered_boston_ward}
        ekeys = {x["Ward"]:{} for x in eligible_boston_ward}

        # Aggregate the voter data of all Precincts by Ward #
        for prec in registered_boston_ward:  # Registered Voters
            for amount in prec:
                if (amount != "Ward") and (amount != "Precinct") and (amount != '_id'):
                    if amount in rkeys[prec["Ward"]]:
                        rkeys[prec["Ward"]][amount] += int(prec[amount].replace(',', ''))
                    else:
                        rkeys[prec["Ward"]][amount] = int(prec[amount].replace(',', ''))

        for prec in eligible_boston_ward:  # Eligible/Non-registered voters
            for amount in prec:
                if (amount != "Ward") and (amount != "Precinct") and (amount != '_id'):
                    if amount in ekeys[prec["Ward"]]:
                        ekeys[prec["Ward"]][amount] += int(prec[amount].replace(',', ''))
                    else:
                        ekeys[prec["Ward"]][amount] = int(prec[amount].replace(',', ''))

        repo['carlosp_jpva_tkay_yllescas.registered_by_ward'].insert_many([rkeys])
        repo['carlosp_jpva_tkay_yllescas.registered_by_ward'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.registered_by_ward'].metadata())

        repo['carlosp_jpva_tkay_yllescas.eligible_by_ward'].insert_many([ekeys])
        repo['carlosp_jpva_tkay_yllescas.eligible_by_ward'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.eligible_by_ward'].metadata())

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
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', './carlosp_jpva_tkay_yllescas')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', './data')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#registered_and_eligible_aggregation',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        registered_data = doc.entity('dat:data#non_registered_Precinct',
                              {'prov:label': 'Eligible voters in all Precincts in MA', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        eligible_data = doc.entity('dat:data#registered_voters_Precinct',
                              {'prov:label': 'Registered voters in all Precincts in MA', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_eligibleWardAggregation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_registeredWardAggregation = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_eligibleWardAggregation, this_script)
        doc.wasAssociatedWith(get_registeredWardAggregation, this_script)

        doc.usage(get_eligibleWardAggregation, eligible_data, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(get_registeredWardAggregation, registered_data, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        eligible_aggregation = doc.entity('dat:/eligible_by_ward', {prov.model.PROV_LABEL: 'Amount of eligible voters in Boston by Ward', prov.model.PROV_TYPE: 'ont:DataSet'})
        registered_aggregation = doc.entity('dat:/registered_by_ward', {prov.model.PROV_LABEL: 'Amount of registered voters in Boston by Ward', prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(eligible_aggregation, this_script)
        doc.wasGeneratedBy(eligible_aggregation, get_eligibleWardAggregation, endTime)
        doc.wasDerivedFrom(eligible_aggregation, eligible_data, get_eligibleWardAggregation, get_eligibleWardAggregation, get_eligibleWardAggregation)

        doc.wasAttributedTo(registered_aggregation, this_script)
        doc.wasGeneratedBy(registered_aggregation, get_registeredWardAggregation, endTime)
        doc.wasDerivedFrom(registered_aggregation, registered_data, get_registeredWardAggregation, get_registeredWardAggregation,
                           get_registeredWardAggregation)

        repo.logout()

        return doc

## eof
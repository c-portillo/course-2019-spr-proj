import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from math import sqrt
from random import shuffle


class p_values(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ['carlosp_jpva_tkay_yllescas.demographics_by_towns', 'carlosp_jpva_tkay_yllescas.voterData2010']
    writes = ['carlosp_jpva_tkay_yllescas.p_values']


    @staticmethod
    def execute(trial=False):
        print("p_values")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        repo.dropCollection("p_values")
        repo.createCollection("p_values")


        # Grab datasets from database
        demographicsByTowns = (repo['carlosp_jpva_tkay_yllescas.demographics_by_towns']).find()
        voterData = (repo['carlosp_jpva_tkay_yllescas.voterData2010']).find()

        vData = []
        demData = []
        X = []
        Y = []

        def permute(x):
            shuffled = [xi for xi in x]
            shuffle(shuffled)
            return shuffled

        # Average
        def avg(x):
            return sum(x) / len(x)

        # Standard Deviation
        def stddev(x):
            m = avg(x)
            return sqrt(sum([(xi - m) ** 2 for xi in x]) / len(x))

        # Covariance
        def cov(x, y):
            return sum([(xi - avg(x)) * (yi - avg(y)) for (xi, yi) in zip(x, y)]) / len(x)

        # Correlation Coefficient
        def corr(x, y):
            if stddev(x) * stddev(y) != 0:
                return cov(x, y) / (stddev(x) * stddev(y))

        # p value
        def p(x, y):
            c0 = corr(x, y)
            corrs = []
            for k in range(0, 2000):
                y_permuted = permute(y)
                corrs.append(corr(x, y_permuted))
            return len([c for c in corrs if abs(c) >= abs(c0)]) / len(corrs)


        for a in demographicsByTowns:
            demData.append(a)

        for b in voterData:
            vData.append(b)

        raceComparisons = ["Hispanic_vs_Registration", "Black_vs_Registration", "White_vs_Registration", "Asian_vs_Registration"]

        pVals = {x:{} for x in raceComparisons}

        # Get hispanic_vs_registration p-value
        for a in demData:  # Registered voters
            registered = ""
            key = a["Community"].lower()
            population = a["Population 2010"].replace(",", "")
            hispanicPop = a["Hispanic"].replace(",", "")

            for j in vData:
                if j["Community"].lower() == key:
                    registered = j["Registered"].replace(",", "")

            hispanicPercent = round((int(hispanicPop) * 100 / int(population)), 2)  # x value
            registeredPercent = round(int(registered) * 100 / int(population), 2)  # y value

            X.append(hispanicPercent)
            Y.append(registeredPercent)

        hispanic_vs_reg_pval = p(X, Y)
        pVals["Hispanic_vs_Registration"]["p-value"] = hispanic_vs_reg_pval
        #print("TEST HISP PVAL: " + str(hispanic_vs_reg_pval))

        # Get black_vs_registration p value
        X = []
        Y = []
        for a in demData:  # Registered voters
            registered = ""
            key = a["Community"].lower()
            population = a["Population 2010"].replace(",", "")
            blackPop = a["Black"].replace(",", "")

            for j in vData:
                if j["Community"].lower() == key:
                    registered = j["Registered"].replace(",", "")

            blackPercent = round((int(blackPop) * 100 / int(population)), 2)  # x value
            registeredPercent = round(int(registered) * 100 / int(population), 2)  # y value

            X.append(blackPercent)
            Y.append(registeredPercent)

        black_vs_reg_pval = p(X, Y)
        pVals["Black_vs_Registration"]["p-value"] = black_vs_reg_pval
        #print("TEST BLACK PVAL: " + str(black_vs_reg_pval))

        # Get white_vs_registration p value
        X = []
        Y = []
        for a in demData:  # Registered voters
            registered = ""
            key = a["Community"].lower()
            population = a["Population 2010"].replace(",", "")
            whitePop = a["White"].replace(",", "")

            for j in vData:
                if j["Community"].lower() == key:
                    registered = j["Registered"].replace(",", "")

            whitePercent = round((int(whitePop) * 100 / int(population)), 2)  # x value
            registeredPercent = round(int(registered) * 100 / int(population), 2)  # y value

            X.append(whitePercent)
            Y.append(registeredPercent)

        white_vs_reg_pval = p(X, Y)
        pVals["White_vs_Registration"]["p-value"] = white_vs_reg_pval
        #print("TEST WHITE PVAL: " + str(white_vs_reg_pval))

        # Get asian_vs_registration p value
        X = []
        Y = []
        for a in demData:  # Registered voters
            registered = ""
            key = a["Community"].lower()
            population = a["Population 2010"].replace(",", "")
            asianPop = a["Asian"].replace(",", "")

            for j in vData:
                if j["Community"].lower() == key:
                    registered = j["Registered"].replace(",", "")

            asianPercent = round((int(asianPop) * 100 / int(population)), 2)  # x value
            registeredPercent = round(int(registered) * 100 / int(population), 2)  # y value

            X.append(asianPercent)
            Y.append(registeredPercent)

        asian_vs_reg_pval = p(X, Y)
        pVals["Asian_vs_Registration"]["p-value"] = asian_vs_reg_pval
        #print("TEST ASIAN PVAL: " + str(asian_vs_reg_pval))

        repo['carlosp_jpva_tkay_yllescas.p_values'].insert_many([pVals])
        repo['carlosp_jpva_tkay_yllescas.p_values'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.p_values'].metadata())

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
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#p_values',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        voter_data = doc.entity('dat:data#voterData2010',
                                     {'prov:label': 'Voter Data 2010',
                                      prov.model.PROV_TYPE: 'ont:DataResource',
                                      'ont:Extension': 'json'})
        demographics_data = doc.entity('dat:data#demographics_by_towns',
                                   {'prov:label': 'Demographics By Towns',
                                    prov.model.PROV_TYPE: 'ont:DataResource',
                                    'ont:Extension': 'json'})

        get_pValues = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_pValues, this_script)

        doc.usage(get_pValues, voter_data, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(get_pValues, demographics_data, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        pValues = doc.entity('dat:/p_values', {prov.model.PROV_LABEL: 'P-Values for race populations and registration rates',
                                               prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAttributedTo(pValues, this_script)
        doc.wasGeneratedBy(pValues, get_pValues, endTime)
        doc.wasDerivedFrom(pValues, voter_data, get_pValues,
                           get_pValues, get_pValues)

        repo.logout()

        return doc

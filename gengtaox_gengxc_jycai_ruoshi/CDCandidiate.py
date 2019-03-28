import requests
import dml
import prov.model
import datetime
import uuid
import zipfile
import xlrd
import os


class CDCandidiate(dml.Algorithm):
    contributor = 'gengtaox_gengxc_jycai_ruoshi'
    reads = []
    writes = ['gengtaox_gengxc_jycai_ruoshi.CDcandidate', ]

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gengtaox_gengxc_jycai_ruoshi', 'gengtaox_gengxc_jycai_ruoshi')

        CDC_dict = []

        CandidiateURL = "http://ocpf2.blob.core.windows.net/downloads/data/registered-candidates.zip"

        r = requests.get(CandidiateURL)
        dir = "gengtaox_gengxc_jycai_ruoshi/"
        fname = "registered-candidates.zip"
        with open(dir + fname, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

        zipf = zipfile.ZipFile(dir + fname)
        filelist = zipf.namelist()

        zipf.extractall(path="gengtaox_gengxc_jycai_ruoshi/xlsx")

        data = xlrd.open_workbook("gengtaox_gengxc_jycai_ruoshi/xlsx/registered-candidates.xlsx")

        table = data.sheets()[1]

        candidiates = [table.col_values(7), table.col_values(8), table.col_values(4), table.col_values(29)]

        for i in range(1, len(candidiates[0])):
            CDC_dict.append({
                "Candidiate FirstName": candidiates[0][i],
                "Candidiate lastName": candidiates[1][i],
                "District Code": candidiates[2][i],
                "District": candidiates[3][i]
            })

        repo.dropCollection("CDcandidate")
        repo.createCollection("CDcandidate")

        repo['gengtaox_gengxc_jycai_ruoshi.CDcandidate'].insert_many(CDC_dict)
        repo['gengtaox_gengxc_jycai_ruoshi.CDcandidate'].metadata({'complete': True})
        print(repo['gengtaox_gengxc_jycai_ruoshi.CDcandidate'].metadata())

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

        doc.add_namespace('ont', 'http://ocpf2.blob.core.windows.net/downloads/registered-candidates.zip')
        # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('ucb', 'http://ocpf2.blob.core.windows.net/downloads/registered-candidates.zip')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:gengtaox_gengxc_jycai_ruoshi#CDcandidate',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource_web = doc.entity('ucb:candidate', {'prov:label': 'Registered Candidates',
                                                prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'xlsx'})

        get_web = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_web, this_script)

        doc.usage(get_web, resource_web, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:DataResource'
                   })

        CDcandidate = doc.entity('dat:gengtaox_gengxc_jycai_ruoshi#CDcandidate',
                           {prov.model.PROV_LABEL: 'Candidate By Congress District', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(CDcandidate, this_script)

        doc.wasGeneratedBy(CDcandidate, get_web, endTime)

        doc.wasDerivedFrom(CDcandidate, resource_web, get_web, get_web, get_web)

        return doc

## eof
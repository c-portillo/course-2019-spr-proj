import requests
import json
import dml
import prov.model
import datetime
import uuid
import csv
import re
import zipfile
import os

class CDMap(dml.Algorithm):
    contributor = 'gengtaox_gengxc_jycai_ruoshi'
    reads = []
    writes = ['gengtaox_gengxc_jycai_ruoshi.CDMap',]

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gengtaox_gengxc_jycai_ruoshi', 'gengtaox_gengxc_jycai_ruoshi')
        
        CD_dict = []
        for i in range(11):
            CD_dict.append({
                "District": i,
                "Map": {}
            })

        url = "https://www.census.gov/geo/maps-data/data/cbf/cbf_cds.html"
        r = requests.get(url)
        mapUrls = re.findall(r'<option value= "(.*)"> Massachusetts</option>', r.text)
        for mu in mapUrls:
            r = requests.get(mu)
            fname = "gengtaox_gengxc_jycai_ruoshi/" + mu.split("/")[-1]

            # store the file in local disk
            with open(fname, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)

            # get the file name of shp file
            zipf = zipfile.ZipFile(fname)
            filelist = zipf.namelist()
            shp_file_name = list(filter(lambda name : name.endswith(".shp"), filelist))[0]

            # extract all the file to its dir
            dir_name = shp_file_name.split(".")[0]
            zipf.extractall(path="gengtaox_gengxc_jycai_ruoshi/" + dir_name)

            # convert the map to GeoJson format
            cmd = "ogr2ogr -f GeoJSON {} {}".format("gengtaox_gengxc_jycai_ruoshi/" + "{}/{}.json".format(dir_name, dir_name), "gengtaox_gengxc_jycai_ruoshi/" + "{}/{}".format(dir_name, shp_file_name))
            os.system(cmd)
            
            if mu.split("/")[-1].startswith("gz"):
                key = "111"
            else:
                key = mu.split("_")[1]

            with open("gengtaox_gengxc_jycai_ruoshi/" + "{}/{}.json".format(dir_name, dir_name),'r') as load_f:
                load_dict = json.load(load_f)

                for feature in load_dict['features']:
                    cd_id = int(feature['properties']['CD'])
                    CD_dict[cd_id]['Map'][key] = feature['geometry']

        CD_dict = CD_dict[1:]
        repo.dropCollection("CDMap")
        repo.createCollection("CDMap")
        
        repo['gengtaox_gengxc_jycai_ruoshi.CDMap'].insert_many(CD_dict)
        repo['gengtaox_gengxc_jycai_ruoshi.CDMap'].metadata({'complete':True})
        print(repo['gengtaox_gengxc_jycai_ruoshi.CDMap'].metadata())

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

        doc.add_namespace('ont', 'https://www.census.gov/geo/') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('ucb', 'https://www.census.gov/geo/')
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:gengtaox_gengxc_jycai_ruoshi#CDMap', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_web = doc.entity('ucb:cdmap', {'prov:label':'Cartographic Boundary Shapefiles', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})

        get_web = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_web, this_script)

        doc.usage(get_web, resource_web, startTime, None,
                  {prov.model.PROV_TYPE:'ont:DataResource'
                  })

        CDMap = doc.entity('dat:gengtaox_gengxc_jycai_ruoshi#CDMap', {prov.model.PROV_LABEL:'Congress District Map', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(CDMap, this_script)

        doc.wasGeneratedBy(CDMap, get_web, endTime)

        doc.wasDerivedFrom(CDMap, resource_web, get_web, get_web, get_web)

        return doc


## eof
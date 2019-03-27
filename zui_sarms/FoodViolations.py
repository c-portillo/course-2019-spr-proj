import datetime
import logging
import uuid

import dml
import pandas as pd
import prov.model

# Is this URL permanent?
log = logging.getLogger(__name__)


class FoodViolations(dml.Algorithm):
    contributor = 'zui_sarms'
    reads = ["zui_sarms.food_inspections"]
    writes = ['zui_sarms.food_violations']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()
        # Set up the database connection.
        # This will fail to connect to the one require SSH auth
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')

        df = pd.DataFrame(list(repo["zui_sarms.food_inspections"].find()))

        # Project to select only the column we wants
        selected_columns = ["businessname", "licenseno", "violstatus", "address", "city", "state", "zip", "property_id",
                            "location"]
        DF = df[selected_columns]

        # Remove the row which has an empty value [x for row in table for x in row if x]
        DF = DF.dropna()

        # Select all the Fail violations
        DF = DF[DF["violstatus"] == "Fail"]

        # Count violations per restaurant
        VC = DF.groupby("licenseno").count()

        DF_R = DF.set_index("licenseno")[["businessname", "address", "city", "state", "zip", "location"]]
        DF_R["violation_count"] = VC["violstatus"]
        DF_R = DF_R.drop_duplicates()

        DF_R["_id"] = DF_R.index.values
        DF_R["location"] = DF_R["location"].map(parse_coor)

        r_dict = DF_R.to_dict(orient="record")

        repo.dropCollection("food_violations")
        repo.createCollection("food_violations")
        repo['zui_sarms.food_violations'].insert_many(r_dict)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:alice_bob#FoodViolations',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:zui_sarms#FoodInspection',
                              {prov.model.PROV_LABEL: 'Food Inspections', prov.model.PROV_TYPE: 'ont:DataSet'})
        get_fv = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fv, this_script)
        doc.usage(get_fv, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'}
                  )
        fv = doc.entity('dat:zui_sarms#FoodViolations',
                        {prov.model.PROV_LABEL: 'Food Establishment Violations', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fv, this_script)
        doc.wasGeneratedBy(fv, get_fv, endTime)
        doc.wasDerivedFrom(fv, resource, get_fv, get_fv, get_fv)

        return doc


def parse_coor(s):
    """
    Parse the string to tuple of coordinate
    In the format of (lat, long)
    """

    lat, long = s.split(", ")
    lat = lat[1:]
    long = long[:-1]
    lat = float(lat)
    long = float(long)

    return [lat, long]

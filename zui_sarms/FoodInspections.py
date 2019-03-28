"""
Pulling data from City of Boston data portal about
[Food Establishment Inspection](https://data.boston.gov/dataset/food-establishment-inspections)

# Resource ID: 4582bec6-2b4f-4f9e-bc55-cbaa73117f4c

"""
import datetime
import io
import logging
import os
import tempfile
import uuid

import dml
import pandas as pd
import prov.model
import requests

log = logging.getLogger(__name__)

RES_ID = "4582bec6-2b4f-4f9e-bc55-cbaa73117f4c"
# Is this URL permanent?
URL = f"https://data.boston.gov/dataset/03693648-2c62-4a2c-a4ec-48de2ee14e18/resource/{RES_ID}/download/tmp1yzpct9p.csv"


class FoodInspections(dml.Algorithm):
    contributor = 'zui_sarms'
    reads = []
    writes = ['zui_sarms.food_inspections']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()
        # Set up the database connection.
        # This will fail to connect to the one require SSH auth
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')

        df = download_csv(URL)

        # Project to select only the column we wants
        selected_columns = ["businessname", "licenseno", "violstatus", "address", "city", "state", "zip", "property_id",
                            "location"]
        DF = df[selected_columns]

        # Remove the row which has an empty value [x for row in table for x in row if x]
        DF = DF.dropna()

        DF["_id"] = DF.index.values

        r_dict = DF.to_dict(orient="record")

        repo.dropCollection("food_inspections")
        repo.createCollection("food_inspections")
        for rr in r_dict:
            repo['zui_sarms.food_inspections'].insert_one(rr)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('alice_bob', 'alice_bob')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:alice_bob#FoodInspection',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:4582bec6-2b4f-4f9e-bc55-cbaa73117f4c',
                              {'prov:label': 'Food Establishment Inspections', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_fi = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fi, this_script)
        doc.usage(get_fi, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:DataSet': '03693648-2c62-4a2c-a4ec-48de2ee14e18/resource/{RES_ID}/download/tmp1yzpct9p.csv'
                   }
                  )
        fi = doc.entity('dat:zui_sarms#FoodInspection',
                        {prov.model.PROV_LABEL: 'Food Inspections', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fi, this_script)
        doc.wasGeneratedBy(fi, get_fi, endTime)
        doc.wasDerivedFrom(fi, resource, get_fi, get_fi, get_fi)

        repo.logout()

        return doc


def download_csv(url):
    """
    Download the file at the URL

    :param str url:
    :return: pandas.DataFrame containing the content of the CSV file
    :rtype: pandas.DataFrame
    """
    temp = download_file(url)

    # After we finished writing the temp-file, we can read it as a CSV file
    temp_io = io.StringIO(temp.decode("utf-8"))
    df = pd.read_csv(temp_io, low_memory=False)

    return df


def download_file(url):
    """
    Download file and return the raw content

    :param url:
    :return:
    """

    rd = RequestsDownloader(raw=True)

    return rd.download(url=url)


def ensure_path_exists(path):
    """
    Make the path if necessary

    :param path:
    """
    dirpath = os.path.abspath(os.path.dirname(path))
    if not os.path.exists(dirpath):
        log.info("Path %s not exists. Making it ourselves!", dirpath)
        os.makedirs(dirpath)
    return path


class BaseDownloader:
    def __init__(self, raw=False):
        self.raw = raw

    def download(self, url, filename=None):
        """
        Download an url
        :param buf: [Optional] Download to a buffer instead
        :param url:
        :param filename:
        :return:
        """

        if not filename:
            filename = self._make_filename(url)
        path = self._make_path(filename)

        if self.raw:
            return self._download(url, path)

        log.info("Downloaded: %s -> %s", url, path)
        return path

    def _download(self, url, path):
        raise NotImplementedError

    @staticmethod
    def _make_path(filename):
        """
        Generate the local system path from filename

        :param filename:
        :return:
        """
        path = os.path.join("/home/zui/kode/gwrdata", filename)
        path = ensure_path_exists(path)
        log.debug("Making path: %s", path)
        return path

    @staticmethod
    def _make_filename(url):
        """
        Make filename from URL

        :param str url:
        :return:
        """
        # This is super naive.
        # Todo: Make filename when the crawler return per site
        # Todo: Make random filename if needed
        filename = url.split("/")[-1]
        log.debug("Making filename: %s -> %s", url, filename)
        return filename


class RequestsDownloader(BaseDownloader):

    def _download(self, url, path):
        log.debug("Downloading %s", url)
        r = requests.get(url)
        if r.ok:
            buf = r.content
        else:
            raise requests.RequestException("Error while downloading file {}".format(url))

        if self.raw:
            return buf

        with open(path, "wb") as f:
            f.write(buf)

        return path

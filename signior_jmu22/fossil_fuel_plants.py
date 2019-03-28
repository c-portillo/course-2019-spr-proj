import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd 
from dateutil.parser import parse
import numpy as np


def sort_aggregate(list):
  for i in range(0, len(list)):
    list[i] = (list[i][0], list[i][1].sort())
  return list
def aggregate(R):
    keys = {r[0] for r in R}
    return [(key, [v for (k,v) in R if k == key]) for key in keys]

def product(R, S):
  return [(t,u) for t in R for u in S]

def select(R, s):
  return [t for t in R if s(t)]

def is_fossil_fuel(row):
  fuel1 = row.get('fuel1')
  if (fuel1 == 'Oil' or fuel1 == 'Gas' or fuel1 == 'Coal' or fuel1 == 'Waste'):
    return True

def commissioning_year(row):
  year = row.get('commissioning_year')
  if (year != 0.0):
    return True

def project(R, p):
  return [p(t) for t in R]

def merge_by_country(dict):
  result = []
  for row in dict:
    country = row.get('country')
    years = []
    if (result.has_key(country)):
      years.append(row.get('year'))
    else:
      result

def get_country_year(row):
  new_row = {}
  new_row['country'] = row.get('country_long')
  new_row['year'] = int(row.get('commissioning_year'))
  return (row.get('country_long'), int(row.get('commissioning_year')))

class fossil_fuel_plants(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = ['signior_jmu22.power_plants']
  writes = ['signior_jmu22.power_plants_established_date_by_country']

  @staticmethod
  def execute(trial = False):
    startTime = datetime.datetime.now()

    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')

    power_plants = list(repo.signior_jmu22.power_plants.find())

    # init pandas dataframe
    df = pd.DataFrame(power_plants)

    # fill all NaN values with 0
    df.fillna(0, inplace=True)

    # convert back to dict
    list_power_plants = df.to_dict(orient='records')

    # select power plants that only use fossil fuels and waste(oil, waste, gas, coal)
    plants_using_fossil_fuels = select(list_power_plants, is_fossil_fuel)

    # select power plants that have comissioning_year 
    plants_ff_with_year = select(plants_using_fossil_fuels, commissioning_year)


    # convert to tuples of country and year
    country_year = project(plants_ff_with_year, get_country_year)

    # aggregate the result and turn it into country and list of years
    agg_country_year = aggregate(country_year)

    final_ds = []
    for entry in agg_country_year:
      row = {}
      row['country'] = entry[0]
      row['years'] = list(set(entry[1]))
      final_ds.append(row)
    # print(final_ds)

     # below block adds the dataset to the repo collection
    repo.dropCollection("power_plants_established_date_by_country")
    repo.createCollection("power_plants_established_date_by_country")
    repo['signior_jmu22.power_plants_established_date_by_country'].insert_many(final_ds)
    repo['signior_jmu22.power_plants_established_date_by_country'].metadata({'complete': True})

    print(repo['signior_jmu22.power_plants_established_date_by_country'].metadata())

    repo.logout()

    endTime = datetime.datetime.now()
    return {"start": startTime, "end": endTime}

  def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')
    doc.add_namespace('alg', 'http://datamechanics.io/algorithm/signior_jmu22') # The scripts are in <folder>#<filename> format
    doc.add_namespace('dat', 'http://datamechanics.io/data/signior_jmu22' ) # The datasets are in <user>#<collection> format
    doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retreival', 'Query', or 'Computation'
    doc.add_namespace('log', 'http://datamechanics.io/log/')

    this_script = doc.agent('alg:signior_jmu22#fossil_fuel_plants', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
    power_plants = doc.entity('dat:signior_jmu22#power_plants', {prov.model.PROV_LABEL:'Global Power Plant Data', prov.model.PROV_TYPE: 'ont:DataSet'})


    get_fossil_fuel_plants = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_fossil_fuel_plants, this_script)

    doc.usage(get_fossil_fuel_plants, power_plants, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})

    fossil_fuel_plants = doc.entity('dat:signior_jmu22#power_plants_established_date_by_country', {prov.model.PROV_LABEL: 'Countries and dates when a power plant was established', prov.model.PROV_TYPE:'ont:DataSet'})
    doc.wasAttributedTo(fossil_fuel_plants, this_script)
    doc.wasGeneratedBy(fossil_fuel_plants, get_fossil_fuel_plants, endTime)
    doc.wasDerivedFrom(fossil_fuel_plants, power_plants, get_fossil_fuel_plants, get_fossil_fuel_plants, get_fossil_fuel_plants)

    repo.logout()

    return doc

# comment this out when submitting
# fossil_fuel_plants.execute()
# doc = fossil_fuel_plants.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

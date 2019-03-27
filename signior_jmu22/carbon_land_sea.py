#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 18:17:14 2019

@author: jeffreymu
"""

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class carbon_land_sea(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = ['signior_jmu22.carbon_emissions', 'signior_jmu22.land_sea']
  writes = ['signior_jmu22.carbon_land_sea']
  
  @staticmethod
  def execute(trial = False):
      startTime = datetime.datetime.now()
      
      client = dml.pymongo.MongoClient()
      repo = client.repo
      repo.authenticate('signior_jmu22', 'signior_jmu22')
      
      
      #creates list of dictionary object
      temp = list(repo.signior_jmu22.carbon_emissions.find())
      df = pd.DataFrame(temp)
      df.fillna(0,inplace=True)
      #print(df.to_dict(orient ="records"))
      carbon_emissions = df.to_dict(orient = "records")
      #print(carbon_emissions)
     
      land_sea = list(repo.signior_jmu22.land_sea.find())
      #project the years column first
      years = [*range(1960,2015)]

      
      #this does aggregation
      

      templist = []
      tempmax = 0
      for x in years:
          for i in carbon_emissions:

              if i.get(str(x)) == None:
                  continue
              else:
                  tempmax += (i.get(str(x)))
   
          tempmean = (tempmax/len(carbon_emissions))
          tempmax= 0
          templist.append({'Year': x, 'C02': tempmean})
      #print(templist)
      
      
      
      land_sea_carbon = carbon_land_sea.product(templist, land_sea)
      land_sea_carbon_select= []
    
      #land_sea_carbon_select = carbon_land_sea.select(land_sea_carbon, lambda t: t[0][0].get("Year") == int(t[0][1].get("Year")))
      
      
      #way to implement sselect & projection
      count = 0
      for i in land_sea_carbon:
         
          if land_sea_carbon[count][0].get("Year") == int(land_sea_carbon[count][1].get("Year")):
             land_sea_carbon_select.append({'Year': land_sea_carbon[count][0].get("Year"), 
                                            'C02': "{0:.2f}".format(land_sea_carbon[count][0].get("C02")),
                                            'Land': land_sea_carbon[count][1].get("Land"),
                                            'Ocean': land_sea_carbon[count][1].get("Ocean")})
          count+=1
      #print (land_sea_carbon_select)
      
      repo.dropCollection("carbon_land_sea")
      repo.createCollection("carbon_land_sea")
      repo['signior_jmu22.carbon_land_sea'].insert_many(land_sea_carbon_select)
      repo['signior_jmu22.carbon_land_sea'].metadata({'complete': True})
      print(repo['signior_jmu22.land_sea'].metadata())
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
    
    this_script = doc.agent('alg:signior_jmu22#carbon_land_sea', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
    resource= doc.entity('dat:land_sea', {'prov:label': 'Sea level and Land Temperature Changes by Year', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
    get_land_sea = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_land_sea, this_script)
    doc.usage(get_land_sea, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retreival'})
    
    carbon_emissions = doc.entity('dat:signior_jmu22#carbon_emissions', {prov.model.PROV_LABEL: 'Carbon Emissions', prov.model.PROV_TYPE: 'ont:DataSet'})
    doc.wasAttributedTo(carbon_emissions, this_script)
    doc.wasGeneratedBy(get_land_sea, carbon_emissions, endTime)
    doc.wasDerivedFrom(carbon_emissions, resource, get_land_sea, get_land_sea, get_land_sea)
    
    repo.logout()
    
    
    return doc
  def union(R, S):
      return R + S

  def difference(R, S):
      return [t for t in R if t not in S]

  def intersect(R, S):
      return [t for t in R if t in S]

  def project(R, p):
      return [p(t) for t in R]

  def select(R, s):
      return [t for t in R if s(t)]
     
  def product(R, S):
      return [(t,u) for t in R for u in S]
 
    
  def aggregate(R, f):
      keys = {r[0] for r in R}
      return [(key, f([v for (k,v) in R if k == key])) for key in keys]

  

  
    
# carbon_land_sea.execute()
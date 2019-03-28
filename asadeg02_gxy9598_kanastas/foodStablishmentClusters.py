import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from bson.code import Code
import time
from sklearn.cluster import KMeans
import numpy as np


class foodStablishmentClusters(dml.Algorithm):
    
    contributor = 'asadeg02_gxy9598'
    reads = ['asadeg02_gxy9598.building_permits', 'asadeg02_gxy9598.active_food_stablishment']
    writes = ['asadeg02_gxy9598.properties_within_most_populated_foodStablishment_cluster']     
  
    @staticmethod
    def execute(trial = False):

        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asadeg02_gxy9598', 'asadeg02_gxy9598')        

        building_permits =  repo.asadeg02_gxy9598.building_permits.find()
        food_stablishments = repo.asadeg02_gxy9598.active_food_stablishment.find()
        
        # Get locations data
        locations = []
        for doc in food_stablishments:
            location = doc['location'].replace('(', '').replace(')', '').split(', ')
            location = [float(location[0]), float(location[1])]            
            locations.append(location)

        # Cluster food stablishments using kmeans 
        kmeans = KMeans(init='k-means++', n_clusters=20, max_iter=1000)
        kmeans_centers = kmeans.fit(locations).cluster_centers_
        kmeans_labels = kmeans.labels_

        # Get the population in each cluster
        clusters_population = {}
        for label in kmeans_labels:
            if label in clusters_population:
                clusters_population[label] += 1
            else:
                clusters_population[label] = 1

        sorted_clusters_population = sorted(clusters_population, key=clusters_population.get, reverse=True)          
        
        # Find buildings in each cluster 
        clusters_buildings = {}  
        for doc in building_permits:            
            location = doc['Location'].replace('(', '').replace(')', '').split(', ')
            if len(location) == 2:
                location = [float(location[0]), float(location[1])]
                min = float("inf")
                closest_center = None
                for i in range(0, len(kmeans_centers)):
                    dist = np.linalg.norm(np.array(kmeans_centers[i])-np.array(location))
                    if dist <= min:
                        min = dist
                        closest_center = i
                if closest_center in clusters_buildings:
                    clusters_buildings[closest_center].append(doc)
                else:
                    clusters_buildings[closest_center] = [doc]
 
        # Get properties in the most populated food stablishment cluster 
        properties_in_most_populated_cluster = None
        for label in sorted_clusters_population:
            if label in clusters_buildings:                
                properties_in_most_populated_cluster = clusters_buildings[label]
                break

        repo.dropCollection('asadeg02_gxy9598.properties_within_most_populated_foodStablishment_cluster')
        repo.createCollection('asadeg02_gxy9598.properties_within_most_populated_foodStablishment_cluster')
        repo["asadeg02_gxy9598.properties_within_most_populated_foodStablishment_cluster"].insert_many(properties_in_most_populated_cluster)
        repo["asadeg02_gxy9598.properties_within_most_populated_foodStablishment_cluster"].metadata({'complete':True})
        print(repo["asadeg02_gxy9598.properties_within_most_populated_foodStablishment_cluster"].metadata())
        print('Find Propeties Within The Most Populated Food Stablsihment Cluster')
        repo.logout()
        endTime = datetime.datetime.now()
        return {"Start ":startTime, "End ":endTime}

      ###############################################################################################################################################
       

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('asadeg02_gxy9598', 'asadeg02_gxy9598')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('cob', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bod', 'http://bostonopendata.boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:asadeg02_gxy9598#foodStablishmentClusters', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})        
        findFoodStablishmentClusters = doc.activity('log:uuid'+ str(uuid.uuid4()), startTime, endTime, 
                                        {'prov:label':'Clusters Food Stablisments and Finds The Properties In The Most Compact Cluster  ', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(findFoodStablishmentClusters, this_script) 
        
        resource_buiding_permits = doc.entity('dat:asadeg02_gxy9598#building_permits', {prov.model.PROV_LABEL:'Buiding Permits', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_food_stablishments = doc.entity('dat:asadeg02_gxy9598#active_food_stablishment', {prov.model.PROV_LABEL:'Food Stablishments', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(findFoodStablishmentClusters, resource_buiding_permits, startTime)
        doc.usage(findFoodStablishmentClusters, resource_food_stablishments, startTime)
        

        properties_within_most_compact_cluster = doc.entity('dat:asadeg02_gxy9598#properties_within_most_populated_foodStablishment_cluster', 
                                       {prov.model.PROV_LABEL:'Properties Within Most Populated FoodStablishment Cluster', prov.model.PROV_TYPE:'ont:DataSet'})

        doc.wasAttributedTo(properties_within_most_compact_cluster, this_script)
        doc.wasGeneratedBy(properties_within_most_compact_cluster, findFoodStablishmentClusters, endTime)
        doc.wasDerivedFrom(properties_within_most_compact_cluster, resource_food_stablishments, findFoodStablishmentClusters, findFoodStablishmentClusters, findFoodStablishmentClusters)
        doc.wasDerivedFrom(properties_within_most_compact_cluster, resource_buiding_permits, findFoodStablishmentClusters, findFoodStablishmentClusters, findFoodStablishmentClusters)
        
        repo.logout()
        return doc






foodStablishmentClusters.execute()
doc = foodStablishmentClusters.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))
## eof

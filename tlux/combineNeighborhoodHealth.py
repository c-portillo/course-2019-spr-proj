import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, Polygon

class combineNeighborhoodHealth(dml.Algorithm):
    contributor = 'tlux'
    reads = ['tlux.Raw_CDC_Health', 'tlux.Raw_Neighborhoods']
    writes = ['tlux.Neighborhood_Health']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets '''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tlux', 'tlux')
        cdc_data = list(repo['tlux.Raw_CDC_Health'].find())
        neighborhood_data = list(repo['tlux.Raw_Neighborhoods'].find())
        neighborhood_poly = {}
        for neighborhood in neighborhood_data:
            geom = neighborhood['geometry']
            if geom['type'] == 'Polygon':
                shape = []
                coords = geom['coordinates']
                for i in coords[0]:
                    shape.append((i[0],i[1]))
                poly = Polygon(shape)
                neighborhood_poly[neighborhood['properties']['Name']] = [poly]
            if geom['type'] == 'MultiPolygon':
                coords = geom['coordinates']
                polys = []
                for i in coords:
                    shape = []
                    for j in i:
                        for k in j:
                            # need to change list type to tuple so that shapely can read it
                            shape.append((k[0],k[1]))
                    poly = Polygon(shape)
                    polys.append(poly)
                neighborhood_poly[neighborhood['properties']['Name']] = polys
        agg = []
        for val in cdc_data:
            coords = val['geolocation']['coordinates']
            point = Point(coords[0],coords[1])
            for neighborhood in neighborhood_poly.keys():
                for poly in neighborhood_poly[neighborhood]:
                    if poly.contains(point):
                        if 'data_value' in val.keys():
                            # health is a projection of the dataset, only want these columns
                            health = {"measure":val['measure'], "data_value":val['data_value'],
                                      "population_count":val['populationcount'], "measureid":val["measureid"]}
                            agg.append({"Neighborhood": neighborhood, **health})
                        break
        repo.dropCollection("Neighborhood_Health")
        repo.createCollection("Neighborhood_Health")
        repo['tlux.Neighborhood_Health'].insert_many(agg)
        repo['tlux.Neighborhood_Health'].metadata({'complete': True})

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}

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
        repo.authenticate('tlux', 'tlux')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:tlux#combineNeighborhoodHealth',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'],
                                 'ont:Extension': 'py'})

        neighborhoods_input = doc.entity('dat:tlux#Raw_Neighborhoods',
                                         {prov.model.PROV_LABEL: 'Neighborhoods Boston',
                                          prov.model.PROV_TYPE: 'ont:DataSet'})

        cdc_input = doc.entity('dat:tlux#Raw_CDC_Health',
                                      {prov.model.PROV_LABEL: 'Health survey data in Boston',
                                       prov.model.PROV_TYPE: 'ont:DataSet'})

        combine_health_neighborhood = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.usage(combine_health_neighborhood, neighborhoods_input, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'})

        doc.usage(combine_health_neighborhood, cdc_input, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'})

        health_neighborhood = doc.entity('dat:tlux#Neighborhood_Health',
                                        {prov.model.PROV_LABEL: 'Health data mapped to its neighborhood',
                                         prov.model.PROV_TYPE: 'ont:DataSet'})

        doc.wasAssociatedWith(combine_health_neighborhood, this_script)
        doc.wasAttributedTo(health_neighborhood, this_script)
        doc.wasGeneratedBy(health_neighborhood, combine_health_neighborhood, endTime)
        doc.wasDerivedFrom(health_neighborhood, neighborhoods_input, combine_health_neighborhood,
                           combine_health_neighborhood, combine_health_neighborhood)
        doc.wasDerivedFrom(health_neighborhood, cdc_input, combine_health_neighborhood,
                           combine_health_neighborhood, combine_health_neighborhood)

        repo.logout()

        return doc

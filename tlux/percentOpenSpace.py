import dml
import prov.model
import datetime
import uuid

class percentOpenSpace(dml.Algorithm):
    contributor = 'tlux'
    reads = ['tlux.Raw_Open_Spaces', 'tlux.Raw_Neighborhoods']
    writes = ['tlux.Percent_OS']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets '''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tlux', 'tlux')
        open_space_data = list(repo['tlux.Raw_Open_Spaces'].find())


        keys = set()
        for val in open_space_data:
            # removes bad namings
            if val['properties']['DISTRICT'] == 'South end':
                val['properties']['DISTRICT'] = 'South End'
            if val['properties']['DISTRICT'] == 'North Dorchester':
                val['properties']['DISTRICT'] = 'Dorchester'
            keys.add(val['properties']['DISTRICT'])
        # Remove for now because don't know how to categorize multi-district
        keys.remove('Multi-District')

        neighborhood_data = list(repo['tlux.Raw_Neighborhoods'].find())

        # districts in open spaces don't map one to one to neighborhood names
        # this is not entirely accurate, these are based on my best estimation
        # down the line will use either addresses or geojson to more accurately
        # categorize where the open spaces are in relation to neighborhoods
        district_to_neighborhood = {
            'Allston-Brighton': ['Allston', 'Brighton'],
            'Central Boston': ['North End', 'Downtown', 'Bay Village',
                               'Leather District', 'Chinatown', 'West End'],
            'Back Bay/Beacon Hill':['Back Bay', 'Beacon Hill'],
            'Fenway/Kenmore':['Fenway', 'Longwood'],
            'South Boston':['South Boston', 'South Boston Water']
        }

        # types below are associated with wildlife and outdoor activity, we select only these
        wanted_types = ["Parkways, Reservations & Beaches", "Parks, Playgrounds & Athletic Fields",
                        "Urban Wilds & Natural Areas", "Community Gardens"]
        agg_open_data = {}

        # performs projection to desired open space types, then aggregates
        # by summing the areas of the open spaces with the same district
        # and open space type
        for key in keys:
            agg_open_data[key] = {}
            for type in wanted_types:
                agg_open_data[key][type] = 0
        for key in keys:
            for val in open_space_data:
                prop = val['properties']
                if prop['TypeLong'] in wanted_types and prop['DISTRICT'] == key:
                    agg_open_data[key][prop['TypeLong']] += prop['ShapeSTArea']

        totals = {}
        # computes total area of each district
        for key in keys:
            totals[key] = 0
            if key in district_to_neighborhood.keys():
                for place in district_to_neighborhood[key]:
                    for neighborhood in neighborhood_data:
                        if neighborhood['properties']['Name'] == place:
                            totals[key] += neighborhood['properties']['ShapeSTArea']
            else:
                for neighborhood in neighborhood_data:
                    if neighborhood['properties']['Name'] == key:
                        totals[key] += neighborhood['properties']['ShapeSTArea']

        # changes open space type totals in each district as a percentage of the
        # total area of that district
        final = []
        for key in keys:
            for type in wanted_types:
                agg_open_data[key][type] = agg_open_data[key][type]/totals[key]
        for key in agg_open_data.keys():
            final.append({"_id": key, **agg_open_data[key]})

        repo.dropCollection("Percent_OS")
        repo.createCollection("Percent_OS")
        repo['tlux.Percent_OS'].insert_many(final)
        repo['tlux.Percent_OS'].metadata({'complete': True})

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
        repo.authenticate('tlux', 'tlux')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:tlux#percentOpenSpace',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        open_space_input = doc.entity('dat:tlux#Raw_Open_Spaces',
                                      {prov.model.PROV_LABEL: 'Open Spaces in Boston',
                                       prov.model.PROV_TYPE: 'ont:DataSet'})

        neighborhoods_input = doc.entity('dat:tlux#Raw_Neighborhoods',
                                   {prov.model.PROV_LABEL: 'Neighborhoods Boston',
                                    prov.model.PROV_TYPE: 'ont:DataSet'})

        compute_percent = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.usage(compute_percent, neighborhoods_input, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'}
                  )
        doc.usage(compute_percent, open_space_input, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation'}
                  )

        percent_OS = doc.entity('dat:tlux#Percent_OS',
                                {prov.model.PROV_LABEL: 'Percent of Open Spaces by District',
                                 prov.model.PROV_TYPE: 'ont:DataSet'}
                                )

        doc.wasAssociatedWith(compute_percent, this_script)
        doc.wasAttributedTo(percent_OS, this_script)
        doc.wasGeneratedBy(percent_OS, compute_percent, endTime)
        doc.wasDerivedFrom(percent_OS, open_space_input, compute_percent,
                           compute_percent, compute_percent)
        doc.wasDerivedFrom(percent_OS, neighborhoods_input, compute_percent,
                           compute_percent, compute_percent)

        repo.logout()

        return doc


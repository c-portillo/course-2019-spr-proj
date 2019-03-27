import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class transformLinkedin(dml.Algorithm):
    contributor = 'emmaliu_yuyangl'
    reads = ['emmaliu_gaotian_xli33_yuyangl.linkedin']
    writes = ['emmaliu_gaotian_xli33_yuyangl.userLocation']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('emmaliu_gaotian_xli33_yuyangl', 'emmaliu_gaotian_xli33_yuyangl')
        
        
        # Get linkedin data 
        linkedinData = repo.emmaliu_gaotian_xli33_yuyangl.linkedin.find()
        jobs = {}
        data=[]
        dataStored=[]
        countchange=0
            
        for data in linkedinData:
            if data['query'] == "amman":
                name = data['name']
                location = data['query']
                job = data['job']
                #print(job)
                currentJob = data['currentJob']
                #print(currentJob)
                if currentJob == '':
                    jobchange = False
                # print(jobchange)
          #      jobs[name] = jobchange

            if jobchange == False:
                    jobs[name] = {'job':job,'currentjob':currentJob,'location':location,'changejob':'yes'}
            if jobchange != False:
                    jobs[name] = {'job':job,'currentjob':currentJob,'location':location,'changejob':'no'}
                    
            if jobs[name]['changejob'] == 'yes':
                countchange+=1

                
        for key,value in jobs.items():
            # print(key)
            dataStored.append({'name':key,'job':value['job'],'currentjob':value['currentjob']})


        # store results into database
        repo.dropCollection("transLinkedin")
        repo.createCollection("transLinkedin")

        for i in dataStored:
            # print(i)
            repo['emmaliu_gaotian_xli33_yuyangl.userLocation'].insert(i)
        repo['emmaliu_gaotian_xli33_yuyangl.userLocation'].metadata({'complete': True})
        print(repo['emmaliu_gaotian_xli33_yuyangl.userLocation'].metadata())

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

        repo.authenticate('emmaliu_gaotian_xli33_yuyangl', 'emmaliu_gaotian_xli33_yuyangl')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/emmaliu_gaotian_xli33_yuyangl')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/emmaliu_gaotian_xli33_yuyangl')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', '')


        this_script = doc.agent('alg:emmaliu_gaotian_xli33_yuyangl#transformLinkedin',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:linkedinapi',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        transform_Linkedin = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transform_Linkedin, this_script)
        doc.usage(transform_Linkedin, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                    }
                  )


        Linkedin = doc.entity('dat:emmaliu_gaotian_xli33_yuyangl#get_linkedin',
                          {prov.model.PROV_LABEL: 'linkedin', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(Linkedin, this_script)
        doc.wasGeneratedBy(Linkedin, transform_Linkedin, endTime)
        doc.wasDerivedFrom(Linkedin, resource, transform_Linkedin, transform_Linkedin, transform_Linkedin)

        repo.logout()

        return doc

# transformLinkedin.execute()
# doc = getTweets.provenance()
# print(doc.get_provn())

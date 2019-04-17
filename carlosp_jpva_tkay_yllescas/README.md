# Growing Voter Engagement in Communities of Color

For this project, we are working with Amplify Latinx and BU Spark! to analyze Massachusetts voting and demographic data to suggest where they should focus their voter turnout efforts in order to get more people of color out to vote.

As our team is responsible for creating only the groundwork for what will be a much large project in the future, the scope of data analyzed will be limited to city council race results among Latinx voters within Boston Wards. However, the code shall be built with modularity in mind in order to allow for all political races within all the geo-political subdivisions within Massachusetts. For the scope of this project, we are starting with 3 private data sets provided by Amplify Latinx:

1. Registered Voter Demographics
   - Senate District
   - Precinct
   - Congressional District
2. Non-Registered Voter Demographics
   - Senate District
   - Precinct
   - Congressional District
3. City Council Race Results (2009-2017)
4. Demographics by Towns

We are combining these data sets to analyze in which wards people are voting more, what percentage of registered voters are voting within those wards, and how many people are not registered to vote. From this, we will extrapolate where voter registration efforts are going to be effective as based on ratios formed from the amount of Registered to Non-Registered voters and Registered voters to Total Votes cast. Ultimately, our goal is to identify which elections are such that more voters showing up would change the result and provide Amplify Latinx with an interactive, embeddable heat map of Massachusetts that will illustrate this data.

To start, we isolated Latinx voter data by Boston Ward from Registered (2a) and Non-Registered (3a) Voter Demographics by Precinct, and then aggregated the precincts by Ward. Then, we generated the total vote difference by Ward for the city council race from the relevant data set (3). From here, we generated the various ratios mentioned earlier to find the Wards with the most disproportionate amount of people who could vote but dont. We used these ratios and race data to create summary statistics about our voting population. Then, we created a constraint satisfaction algorithm. The constraints used are a flip percentage, predicting how effective canvassing efforts would be, flip goal, and proportion of hispanic people in a ward (generated in the statistical analysis). This algorithm generates visits by which Amplify could flip the entire race, in the fewest number of wards. Finally, we used the Google Geocoding API to transform Demographics by Towns (4) into the geocoding information necessary to use in the map. When we produce the map for Amplify Latinx, the user will be able to input their confidence in how effective their outreach efforts will be (ex. a user might predict that they can flip the votes of 50% of people they reach) and a constraint for desired Latinx percentage in the communities they visit. Then, they will be provided a suggestion of wards to visit as well as the ability to hover over the map and view stats for the different wards.

## course-2019-spr-proj

In this project, you will implement platform components that can obtain a some data sets from web services of your choice, and platform components that combine these data sets into at least two additional derived data sets. These components will interact with the backend repository by inserting and retrieving data sets as necessary. They will also satisfy a standard interface by supporting specified capabilities (such as generation of dependency information and provenance records).

**This project description will be updated as we continue work on the infrastructure.**

## MongoDB infrastructure

### Setting up

We have committed setup scripts for a MongoDB database that will set up the database and collection management functions that ensure users sharing the project data repository can read everyone's collections but can only write to their own collections. Once you have installed your MongoDB instance, you can prepare it by first starting `mongod` _without authentication_:
```
mongod --dbpath "<your_db_path>"
```
If you're setting up after previously running `setup.js`, you may want to reset (i.e., delete) the repository as follows.
```
mongo reset.js
```
Next, make sure your user directories (e.g., `alice_bob` if Alice and Bob are working together on a team) are present in the same location as the `setup.js` script, open a separate terminal window, and run the script:
```
mongo setup.js
```
Your MongoDB instance should now be ready. Stop `mongod` and restart it, enabling authentication with the `--auth` option:
```
mongod --auth --dbpath "<your_db_path>"
```

### Working on data sets with authentication

With authentication enabled, you can start `mongo` on the repository (called `repo` by default) with your user credentials:
```
mongo repo -u alice_bob -p alice_bob --authenticationDatabase "repo"
```
However, you should be unable to create new collections using `db.createCollection()` in the default `repo` database created for this project:
```
> db.createCollection("EXAMPLE");
{
  "ok" : 0,
  "errmsg" : "not authorized on repo to execute command { create: \"EXAMPLE\" }",
  "code" : 13
}
```
Instead, load the server-side functions so that you can use the customized `createCollection()` function, which creates a collection that can be read by everyone but written only by you:
```
> db.loadServerScripts();
> var EXAMPLE = createCollection("EXAMPLE");
```
Notice that this function also prefixes the user name to the name of the collection (unless the prefix is already present in the name supplied to the function).
```
> EXAMPLE
alice_bob.EXAMPLE
> db.alice_bob.EXAMPLE.insert({value:123})
WriteResult({ "nInserted" : 1 })
> db.alice_bob.EXAMPLE.find()
{ "_id" : ObjectId("56b7adef3503ebd45080bd87"), "value" : 123 }
```
If you do not want to run `db.loadServerScripts()` every time you open a new terminal, you can use a `.mongorc.js` file in your home directory to store any commands or calls you want issued whenever you run `mongo`.

## Other required libraries and tools

You will need the latest versions of the PROV, DML, and Protoql Python libraries. If you have `pip` installed, the following should install the latest versions automatically:
```
pip install prov --upgrade --no-cache-dir
pip install dml --upgrade --no-cache-dir
pip install protoql --upgrade --no-cache-dir
```
If you are having trouble installing `lxml` in a Windows environment, you could try retrieving it [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/).

Note that you may need to use `python -m pip install <library>` to avoid issues if you have multiple versions of `pip` and Python on your system.

## Formatting the `auth.json` file

The `auth.json` file should remain empty and should not be submitted. When you are running your algorithms, you should use the file to store your credentials for any third-party data resources, APIs, services, or repositories that you use. An example of the contents you might store in your `auth.json` file is as follows:
```
{
    "services": {
        "cityofbostondataportal": {
            "service": "https://data.cityofboston.gov/",
            "username": "alice_bob@example.org",
            "token": "XxXXXXxXxXxXxxXXXXxxXxXxX",
            "key": "xxXxXXXXXXxxXXXxXXXXXXxxXxxxxXXxXxxX"
        },
        "mbtadeveloperportal": {
            "service": "http://realtime.mbta.com/",
            "username": "alice_bob",
            "token": "XxXX-XXxxXXxXxXXxXxX_x",
            "key": "XxXX-XXxxXXxXxXXxXxx_x"
        }
    }
}
```
To access the contents of the `auth.json` file after you have loaded the `dml` library, use `dml.auth`.

## Running the execution script for a contributed project.

To execute all the algorithms for a particular contributor (e.g., `alice_bob`) in an order that respects their explicitly specified data flow dependencies, you can run the following from the root directory:
```
python execute.py alice_bob
```
To execute the algorithms for a particular contributor in trial mode, use the `-t` or `--trial` option:
```
python execute.py alice_bob --trial


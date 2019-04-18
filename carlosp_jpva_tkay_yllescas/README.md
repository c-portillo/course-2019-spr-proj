# Growing Voter Engagement in Communities of Color

_by Carlos Portilla, JP Vasquez, Tallulah Kay, Gabriel Yllescas_

## Abstract

For this project, we are working with Amplify Latinx and BU Spark! to analyze Massachusetts voting and demographic data to suggest where they should focus their voter turnout efforts in order to get more people of color out to vote.

As our team is responsible for creating only the groundwork for what will be a much large project in the future, the scope of data analyzed will be limited to city council race results among Latinx voters within Boston Wards. However, the code shall be built with modularity in mind in order to allow for all political races within all the geo-political subdivisions within Massachusetts. 

## Data Import

For the scope of this project, we are starting with 3 private data sets provided by Amplify Latinx:

1. `Registered Voter Demographics`
   - Senate District
   - Precinct
   - Congressional District
2. `Non-Registered Voter Demographics`
   - Senate District
   - Precinct
   - Congressional District
3. `City Council Race Results (2009-2017)`
4. `Demographics by Towns`

We are combining these data sets to analyze in which wards people are voting more, what percentage of registered voters are voting within those wards, and how many people are not registered to vote. From this, we will extrapolate where voter registration efforts are going to be effective as based on ratios formed from the amount of Registered to Non-Registered voters and Registered voters to Total Votes cast. Ultimately, our goal is to identify which elections are such that more voters showing up would change the result and provide Amplify Latinx with an interactive, embeddable heat map of Massachusetts that will illustrate this data.

## Data Transformations

To start, we isolated Latinx voter data by Boston Ward from `Registered Voter Demographics` (2a) and `Non-Registered Voter Demographics`  (3a) by `Precinct`, and then aggregated the precincts, by ward. Then, we generated the total vote difference by ward for the city council race from the `City Council Race Results (2009-2017)` (3). From here, we generated the various ratios mentioned earlier to find the wards with the most disproportionate amount of people who could vote but dont. 

## Constraint Satisfaction Algorithm (Greedy Algorithmn)

We used these ratios and race data to create summary statistics about our voting population. Then, we created a constraint satisfaction algorithm. The constraints used are a flip percentage, predicting how effective canvassing efforts would be, flip goal, and proportion of hispanic people in a ward (generated in the statistical analysis). This algorithm generates visits by which Amplify could flip the entire race, in the fewest number of wards. 

## Statistical Analysis

Finally, we used the `Google Geocoding API` to transform `Demographics by Towns` (4) into the geocoding information necessary to use in the map. When we produce the map for Amplify Latinx, the user will be able to input their confidence in how effective their outreach efforts will be (ex. a user might predict that they can flip the votes of 50% of people they reach) and a constraint for desired Latinx percentage in the communities they visit. Then, they will be provided a suggestion of wards to visit as well as the ability to hover over the map and view stats for the different wards.

## Plans For Visualization

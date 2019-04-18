# Growing Voter Engagement in Communities of Color

_by Carlos Portilla, JP Vasquez, Tallulah Kay, Gabriel Yllescas_

## Abstract

For this project, we are working with [Amplify Latinx][amplify] and [BU Spark!][spark] to analyze Massachusetts voting and demographic data to suggest where they should focus their voter turnout efforts in order to get more people of color out to vote.

As our team is responsible for creating only the groundwork for what will be a much large project in the future, the scope of data analyzed will be limited to city council race results among Latinx voters within Boston Wards. However, the code shall be built with modularity in mind in order to allow for all political races within all the geo-political subdivisions within Massachusetts. 

## Data Import

For the scope of this project, we are primarily using 4 private data sets, provided by Amplify Latinx:

1. `Registered Voter Demographics`
   - Senate District
   - Precinct
   - Congressional District
2. `Non-Registered Voter Demographics`
   - Senate District
   - Precinct
   - Congressional District
3. `City Council Race Results (2009-2017)` [source][results]
4. `Demographics by Towns` [source][dems]

## Data Transformations

We are combining these data sets to produce 3 metrics: in which wards people are voting more, what percentage of registered voters are voting within those wards, and how many people are not registered to vote. From this, we will extrapolate where voter registration efforts are going to be effective as based on ratios formed from the amount of registered to non-registered voters and registered voters to total votes cast. Ultimately, our goal is to identify which elections are such that more voters showing up would change the result and provide Amplify Latinx with an interactive, embeddable heat map of Massachusetts that will illustrate this data.

To do so, we isolated Latinx voter data by Boston Ward from `Registered Voter Demographics` and `Non-Registered Voter Demographics` by `Precinct`, and then aggregated the precincts, by ward. Then, we generated the total vote difference by ward for the city council race from the `City Council Race Results (2009-2017)`. From here, we generated the aforementioned ratios to find the wards with the most disproportionate amount of people who could vote but dont. 

## Statistical Analysis

We used these ratios and race data to create summary statistics about our voting population. These summary statistics act as a data sample to guage the demographics of the voters. Using both `Registered Voter Demographics` and `Eligible Voter Demographics`, we produced several statistics comparing all products of registered and eligible, Latinx and otherwise voters. These statistics are stored as `sampling`, and then used as a constraint for choosing which wards to visit. We can choose which statistic to prioritize in our suggestions for where to focus voter turnout efforts.

## Constraint Satisfaction (Greedy Algorithm)

The constraints used are a flip percentage, predicting how effective canvassing efforts would be, flip goal, and proportion of hispanic people in a ward (generated in the statistical analysis). This algorithm generates visits by which Amplify could flip the entire race, in the fewest number of wards. The algorithms sorts wards by descending number of registered voters who didn't turn out. Then, for each ward, it checks if the ward satisfies the constraints, prioritizing the hispanic proportion constraint. If the ward meets the constraints, it is added to `wards_to_visit`.

## Plans For Visualization

We used the `Google Geocoding API` to transform `Demographics by Towns` into the geocoding information necessary to produce an interactive map for Amplify Latinx. The map will be demarcated by wards that will reveal statistical information when hovered over. The user will also be able to input their confidence in how effective their outreach efforts will be ex. a user might predict that they can flip the votes of 50% of people they reach) and a constraint for desired Latinx percentage in the communities they visit. We will be provide a suggestion of wards to visit based on the user's constraints.

[amplify]: https://amplifylatinx.co/
[spark]: http://www.bu.edu/spark/
[results]: https://www.boston.gov/sites/default/files/2017_-_11-07-17_-_city_councillor_at_large_ward_precinct_results.pdf?fbclid=IwAR0FimlNPxQ1WkOBau8nOWlXGUCU_A_gtFel71KmKQkuUC7xnEVlBjGF-6I
[dems]: http://archive.boston.com/news/local/massachusetts/graphics/03_22_11_2010_census_town_population/?fbclid=IwAR1-4mbJ6MZbR9u2sNwsebbWGTaEo3pDR3wJjjAonrZEJhm1EbQz6i0mrW0

# Growing Voter Engagement in Communities of Color

_by Carlos Portillo, Jean P. Vazquez, Tallulah Kay, Gabriel Yllescas_

## Abstract

The United States is a country which was founded on a government elected by the people. It is a concept so integral to what it means to be an American that even the word “American” is often conflated with terms such as freedom of choice. As such, it is very surprising that among all other democratic, well-developed countries, the United States consistently places near the bottom  in terms of voter turnout at an average of 60% . However, this value is not very useful by itself and in order to obtain a better idea of how to improve the United States’ voter turnout rate, one must also take into account race . In the United States, the racial groups with the highest average voter turnout are non-Hispanic whites and African-Americans with rates between 50-65%. On the other hand, Minorities such as Hispanics and all other racial groups not previously mentioned (i.e. Asian, Native American, Pacific Islander, etc.) consistently have a voter turnout rate between 30-45%. As such, the best way to move towards higher turnout rates must begin with increasing voter turnout among these groups. This is especially so given that Hispanics and other Minorities make up almost 17% of the American population, which translates to 43 million people, 30 million of which aren’t voting.  

The goal of this project is to create an interactive map of Massachusetts to help guide groups seeking to increase voter engagement towards where they should focus their efforts in order to get more people of color out to vote. Our team, in conjunction with Amplify Latinx and BU Spark!, plans to accomplish this by analyzing voting and demographic data in order to find geopolitical subdivisions (i.e. wards, precincts, etc.) that have many people who can vote or can register to vote but don’t end up participating. As our team is responsible for creating only the groundwork for what will be a much larger project in the future, the scope of data analyzed will be limited to city council race results among Latinx voters within Boston Wards. However, the code shall be built with modularity in mind in order to allow for all political races within all the geo-political subdivisions within Massachusetts.


## Data Import

For the scope of this project, we are using 5 data sets, two of which are public that we found through our own research, and three private data sets which were provided by Amplify Latinx:

1. [`City Council Race Results (2009-2017)`][results]
2. [`Demographics by Towns`][dems]
3. Massachusetts Early Voting Data
4. `Registered Voter Demographics`
   - Senate District
   - Precinct
   - Congressional District
5. `Non-Registered Voter Demographics`
   - Senate District
   - Precinct
   - Congressional District

## Data Transformations

Two main sets of data transformations were performed on the data obtained above. The first is an aggregation and projection of the data in Registered and Non-Registered Voter Demographics in order to isolate the race and age data for voters only within Boston Wards. The second is a series of aggregations using the City Council Race Results data set to calculate both the overall and by Ward difference in votes between the first and second place candidate. This “difference to flip” was calculated by first aggregating the number of voters in each Ward by the candidate they voted for in order to find who came in first and second place overall. Then we obtained the difference between the two highest totals to obtain the “total difference to flip”, which refers to the total amount of votes the second person would need in order to flip the race. This was then also done for each ward to generate a list titled “diff by ward” containing the difference between the amount of votes obtained in that ward by the winner and runner-up candidates. 

## Statistical Analysis

The first set of statistics used in the visualization comprise several values generated from a statistical analysis of the population data for registered and eligible voters. The values generated both for each ward and overall are: 
   -The proportion of the total population which are Hispanic
   -Proportion of Hispanic people which are eligible
   -Proportion of Hispanic people which are registered
   -Average and standard deviation of Hispanic voters which are registered or eligible in each war
   
The reason why we gather these values are to then use as a constraint for the algorithm in the last phase by choosing which statistic to prioritize in our suggestions for where to focus voter turnout efforts. However, given this project’s limited scope, we will not give the option to prioritize anything other than the proportion of total Hispanics. 

## Constraint Satisfaction and Optimization

As mentioned previously, the goal of the algorithm is to generate a list of suggested Wards to visit and it does so through a two-step process. The first step consists of identifying the Wards that meet the constraint criteria. While the second step is to then generate an optimal result by minimizing the amount of wards that would need to be visited to flip the entire race. The criteria for the first step are the proportion of Hispanic people in a Ward, regardless of whether they voted or are registered and the particular race and geopolitical subdivision that the algorithm should be run on. Given the scope of this project, this second constraint will be locked to Ward results for the Boston City Council race of 2017. After generating the list of Wards which fit these constraints, the algorithm will then generate the amount of registered voters which could be flipped in each Ward as based on the user input variable dubbed “flip percentage”. The “flip percentage” refers to the percentage of registered voters that didn’t vote which a particular campaigning group believes they can convince to vote for the runner-up candidate. Then, using this list, the Wards are sorted in descending order by number of registered voters who didn’t vote and are added to the final list of wards to visit one by one until the amount “flipped voters” exceeds the amount of votes necessary to flip the entire race.  

## Results and Visualization

With this project, the main problem that we sought to solve was to increase voter turnout by targeting areas with a large Hispanic population. However, even after looking at various statistics which indicate a correlation between race and voter registration/turnout, we first sought to confirm whether this was the case within our dataset. As a result, as can be seen in below, we found this to also be the case for Wards in Boston. 
![PNG Image](https://github.com/tallulahkay/course-2019-spr-proj/blob/master/carlosp_jpva_tkay_yllescas/Final%20Results/relationship.jpeg)

Following this, we then began working and by using the approach and tools detailed above, created a visualization on a local Flask server as shown in figures 2 and 3.  

![websiteDef](https://github.com/tallulahkay/course-2019-spr-proj/blob/master/carlosp_jpva_tkay_yllescas/Final%20Results/website_default.jpeg)


![websiteSuggest](https://github.com/tallulahkay/course-2019-spr-proj/blob/master/carlosp_jpva_tkay_yllescas/Final%20Results/website_suggestion.jpeg)


### Reference
For more information on anything mentioned here, please reference the final report document within the Final Results Folder above.


[amplify]: https://amplifylatinx.co/
[spark]: http://www.bu.edu/spark/
[results]: https://www.boston.gov/sites/default/files/2017_-_11-07-17_-_city_councillor_at_large_ward_precinct_results.pdf?fbclid=IwAR0FimlNPxQ1WkOBau8nOWlXGUCU_A_gtFel71KmKQkuUC7xnEVlBjGF-6I
[dems]: http://archive.boston.com/news/local/massachusetts/graphics/03_22_11_2010_census_town_population/?fbclid=IwAR1-4mbJ6MZbR9u2sNwsebbWGTaEo3pDR3wJjjAonrZEJhm1EbQz6i0mrW0

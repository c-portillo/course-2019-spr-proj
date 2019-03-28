# Project #1

**Duy Nguyen** and **Sarah M'Saad**

## How to run this code?

### About mongoDB
- If the mongoDB is not running on the localhost, like how this code initially set-up, there must be an ssh tunnel to the server. 
`ssh -L 27017:localhost:27017 user@example.org`

## Choice of Datasets/Services

- From Analyze Boston:
    - Food Inspection (Violation)
    - Opens Spaces (Parks)
    - Boston Landmarks
- From Yelp API:
    - Businesses Around Boston (Restaurant/Bars)
- From MBTA API:
    - MBTA Stops
- From Google Maps Geocoding API
    - Locations for interesting_spaces

## Objective of these Datasets:
Imagine yourself in the Boston Area for only 24 hours. You want to take advantage of your time and make the most out of your trip. By entering a cuisine you're interested in and a particular neighbourhood, we're able to plan the perfect day without any inconveniences. Firstly, a list of restaurants that are hygenic (can't afford food poisining). We ensure this by analyzing the Food Inspection Dataset and utilizing Yelp Services (this could also be sorted by price point). Secondly, by using MBTA stops, we provide you transportation information/options from and to your destination. Lastly, we provide a list of scenic spaces/historical landmarks so that you get to experience Boston's culture in that particular area.

## Transformations:
==================
1. food_inspection: we aggregated the food inspection dataset by location as the key to calculate the sum of food inspection violations. (The original has every published food inspection violation by datetime.)
2. close_stop: utilizing both `yelp_business` and `mbta_stops` datasets, we compile a new dataset `close_stop` that contains the closest mbta stop for each business around the boston area. Specifically, we calculate the distance by longitude and latitude between each stop and restaurant then append the smallest distance.
3. interesting_spaces: the act of combining `landmarks` and `parks` to create a new dataset with a concise schema. We transform this merged dataset by providing additional information from Google Maps API. The original datasets don't provide the longitude and latitude of these landmarks/parks so we filled in the blanks.
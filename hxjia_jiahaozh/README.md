
# CS504 Data-Mechanics Project 1

## Authors
Haoxuan Jia(hxjia@bu.edu)
Jiahao Zhang(jiahaozh@bu.edu)

## Datasets
### Boston Airbnb Calendar
A csv file containing the price on a cetain day between year 2016 and 2017
<br />http://datamechanics.io/data/hxjia_jiahaozh/Calendar.csv
### Boston Airbnb Listings
A csv file containing detailed information about a house
<br />http://datamechanics.io/data/hxjia_jiahaozh/Listings.csv
### Boston Airbnb Reviews
A csv file containing reviews given by users to a specific house
<br />http://data.insideairbnb.com/united-states/ma/boston/2019-01-17/data/reviews.csv.gz
### Boston Landmarks
A csv file containing landmarks in different neighborhoods of Boston
<br />http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.csv
### US Holidays
A csv file containing date and holidays from 1966 to 2011
<br />http://datamechanics.io/data/hxjia_jiahaozh/US_Holidays.csv

## Purpose
With the datasets above, we can combine them to answer 3 interesting questions:
<br />1.	What is the impact of holidays on the prices of Boston Airbnb houses? Is there any pattern that the average price is highest or lowest on some holiday?
<br />2.	What is the impact of Boston landmarks on the number of houses and on the average prices of houses?
<br />3.	What is the relationship between the prices of houses and traveler's reviews.

## Data Transformation
### Price_and_Comments
Generated from Boston Airbnb Listings and Boston Airbnb Reviews
<br />Boston Airbnb Listings: Project to get data in a form of (listing_id, price, review_score)
<br />Boston Airbnb Reviews: Project to get data in a form of (listing_id, comments);
                             Aggregate to get a combination of comments for each listing_id
<br />Combination: product + Project to get the comments and review score for each listing_id, in the form of (listing_id, price, comments, review_score)
### Price_on_Holidays
Generated from Boston Airbnb Calendar and US_Holidays
<br />Boston Airbnb Calendar: Select the data with valid price;
                        Project to get data in a form of (date, price);
                        Aggregate to get the mean price for each date
<br />US_Holidays: Select holidays in the range of Boston Airbnb Calendar's dates
<br />Combination: Product + Project to get the mean price for each date and whether the date is a holiday, in the form of (date, avg_price, holiday)
### Prices_Landmarks_Listings
Generated from Boston Airbnb Listings and Boston Landmarks
<br />Boston Airbnb Listing: Select, Project  Aggregate to get (neighbourhood, the number of houses in that neighbourhood ), Select, Project and Aggregate to get (neighbourhood, the mean price of houses in that neighbourhood).
<br />Boston Landmarks: Select, Project and Aggregate to get (neighbourhood, the number of landmarks in that neighbourhood)
<br />Combiantion: project to get  (neighbourhood, the number of landmarks,  the number of houses, the mean prices of houses in that neighbourhood )
## Tools and Libraries
Pandas
<br />dml
<br />prov
<br />protoql
<br />json
<br />uuid
<br />urllib.request

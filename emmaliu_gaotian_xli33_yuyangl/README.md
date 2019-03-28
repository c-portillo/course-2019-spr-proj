# CS504 Project #1 - Mapping Amman
***This project is a part of [BU Spark!](http://www.bu.edu/spark/) project “Mapping Amman”.***

## Introduction
Prof.Anderson of BU history department is conducting an ethnography of present-day Amman, Jordan, to determine how 22-35 year olds with university degrees, who are living in representative neighborhoods around the city are navigating the neoliberal development projects financed by the state.  In just the last two decades, Amman has doubled in size, and schooling, jobs and entertainment have been privatized. The youth population is the first generation to be fully immersed in this new city, facing its new obstacles and opportunities. 

2 big topics to guide the project:

- Using the intersection of social media and mapping, where do people spend their time? Is it feasible to get to these places, and are these places conducive to networking and socializing in affordable ways? Are people happy when they are in these places? If not, what are the conditions when they are not happy?

- Can we find a relationship between university degrees, skills, language, and English training centers, and whether or not a person in Amman has a job?

## Milestone #1
- Scrape data from social media and store them in [MongoDB](https://www.mongodb.com/).
- Do some data transformation.
- Analyze results and discuss them with the project partner.

## Our Works
Because our project partener do not provide us with the data, so our work focused more on how to get the useful data for the project. **We have discussed this with Prof. Andrei and he understood this and reduced the requirements for transformation for our Project #1.**

### 1. Scrape Data
Following the two topics mentioned above, out first step is getting data since we are not provided with data sets from the project partner. We decide to get data from [Twitter](https://twitter.com/?lang=en) and [LinkedIn](https://www.linkedin.com/).

- **Twitter**

  At first, we want to use [Twitter API](https://developer.twitter.com/content/developer-twitter/en.html) to get users who live in Amman and then get their tweets. However, the API do not provide this fuction and we cannot directly get all the users with location "Amman" in their profile. Hence, we decide to get tweets with location "Amman". We set the coordinates of the center of Amman and the radius to specify the range and get the tweets in that area. We get 5,000 tweets, store all the information as a [JSON](https://www.json.org/) file and upload it to [the course website](http://datamechanics.io/data/tweets_amman.json). **Due to the execute.py will run all Python file in subdirectory, we upload the source code for getting tweets in crawlTweets.pdf.**

- **LinkedIn**

  According to the project topic, we mainly focus on people who are from Amman (Jordan) and their education as well as job. We use an API called [Linkedin Search
Export](https://phantombuster.com/api-store/3149/linkedin-search-export) to run through people’s profiles on Linkedin. We only get around 150 sets of data and upload it to [the course website](http://datamechanics.io/data/linkedindataset.json) as well. The limitaion will be discussed later.

### 2. Data Transformation
- **Twitter**

1. Filter out the tweets that the user's location is not empty.
2. Do the aggregation transformation on the location in the user's profile
3. Calculate the number of people who posted the tweets within Amman for each location where these people come from.
4. Calculate the average number of followers and friends for users in these location.

- **LinkedIn**

1. Do the aggregation transformation on the query on the dataset.
2. According to the current job, calculate the number of people who changed their jobs.
3. Do the project transformation to get the data we need.

### 3. Analysis and Discussion
- **Analysis for Twitter**

  The data set we get includes some useful information, such as the location of the users. By analyzing that, we find that there are basically two types of people: native and tourists and there are some difference in their number of followers and friends. About 60% of them are tourists. But there are still some people who do not specify their location in their profile. Also, some texts are in Arabic, so we maybe need to translate them into English later.

- **Analysis for LinkedIn**

  We find that there are only a few people who come from Amman in our LinkedIn data set. There are some limitaions related to LinkedIn itself. First, Linkedin only allows up to three degrees of friend relationship to see other people’s profile. As we are both from China and currently studying in US, we do not have lots of friends or know anyone who is from Jordan. Therefore, we do not have deep exposure to view these profiles of people who are from Amman. Second, we can only scrape up to 100 profiles once without premium membership, which would limit our dataset size. Third, some people do not post their educational backgrounds on their Linkedin profiles. It is understandable in some sense that these people probably are not students or recent graduates. Lastly, when we tried to use Amman as query to scrape, some locations in these people’s profiles are neither Jordan or Amman, which is not related to the main purpose of the project. According to http://gs.statcounter.com/social-media-stats/all/jordan, LinkedIn is not a popular social media in Jordan. Therefore, the final results we get is reasonable.

- **Discussion with project partner**

  Based on analysis above, we have a meeting with our project partner on March 7, 2019. We make on agreement that we do not use Linkedin as a sources since there are too many problems in the data set. We will focus on Twitter for our project. Our next goal is to split users who send tweets in Amman into three groups: native, tourist and unknown and try to find more information for each group. If the results is good, we will get more tweets and do sentimental analysis for those tweets.
  
 ## Reference
 - https://developer.twitter.com/en/docs.html
 - https://www.json.org/
 - http://cs-people.bu.edu/lapets/504/

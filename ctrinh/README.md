# ctrinh

Subfolder for Christopher Trinh in the Spring 2019 iteration of the Data Mechanics course at Boston University.

## External Dependencies
* `pandas` module

## Project 1

The idea that I was pursuing in this project was the notion of how the weather influences transportation, whether it be cars, bikes, or even trains. I was hoping that by finding examining monthly weather and climate data along with the usage levels of different modes of transportation, an analysis could be performed discerning the different kinds of transportation in relation to the type of weather.

To achieve this, I used five distinct datasets:
* Monthly Boston weather from 2018 and 2015 (`weather.py`)
* MBTA train data (`mbta.py`)
* Monthly Uber trip usage from 2018 (`uber.py`)
* Monthly Bluebike trip duration from 2018 (`bluebikes.py`)
* Monthly cars parked at parking lots from 2015 (`parking.py`)

After gathering each of these datasets and storing them in MongoDB, I then transformed the weather dataset and combined them with projections of the Uber, Bluebike, and parking datasets. This created `reWeatherUber.py`, `reWeatherBluebike.py`, and `reWeatherParking.py` respectively. The idea was that each of these three distinct transformed datasets can be used to examine the correlation (if any) between weather and the usage levels of each mode of transportation examined in each data set.

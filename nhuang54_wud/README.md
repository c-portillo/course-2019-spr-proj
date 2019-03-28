# Project 1
##### Nuan Huang and Dennis Wu (nhuang54_wud)


## Narrative

Nuan and Dennis are avid bikers in the wonderful city of Boston. 

As bikers, we're always aware of certain risks that this form of transportation contains: unsafe roads, bike crashes, bike theft, and more. So, in order to make the city of Boston a better place for bikers, we decided to focus our project on analyzing data on bikes and biking conditions.

One major question we focused on was: How safe is Boston for bikers, and why? In order to understand the problem, we started by analyzing crashes and deaths in Boston. Using Vision Zero's data on crashes and deaths, we examined biking accidents and possible causes. Maybe there was a lack of a traffic light at an intersection that caused an accident, or not enough streetlights, leading to a car crashing into a bike.

Using our data sets, we tried to examine all possible causes of things that could've caused danger for bikers.

---

## Our Data Sets
Data Set|Description
-|-
Fatality Record | Data from Vision Zero that provides statistics on death by transportation in Boston (pedestrian, biking, vehicle deaths).
Crash Record | Data from Vision Zero that provides statistics on recent crashes in Boston (car crashes, bike crashes, more).
Hubway Stations | Data provided by Hubway that shows the locations for every Hubway bike station in Boston.
Streetlight Locations | Data provided by the Department of Innovation and Technology that describes over 74,000 streetlights in Boston (locations, etc.)
Traffic Signal Locations | Data provided by the Department of Innovation and Technology that gives information on all of Boston's traffic signals.

---

## Transformations
- transformBikeCrash.py
- transformFatalIntersections.py
- transformHubwayCrash.py

### Usage
Data sets and transformations are completed by doing:

```python
python execute.py nhuang54_wud
```

3 new datasets will be created in the `nhuang54_wud/new_datasets` folder.

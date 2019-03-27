I gathered data from Massachusetts local and regional school districts to summarize some statistics that can help visualize public education and availability of educational resources in Massachusetts. First, I computed the number of districts with average class sizes of less than 10, 10-19, 20-29, and 30+ students (in the collection "sizecategories". Then, I computed the number of districts in each of those categories for districts that offered grades 9-12 and that didn't offer grades 9-12 (in the collection "sizecategorieshs". Finally, I geocoded all public libraries in Massachusetts based on an online list of public libraries, and determined how many public libraries fell in the geographic bounds of each school district (in the collection "libperdistr"). Based on the variation in these results, we could formulate hypotheses based on the number of libraries, grades offered, and class size within a school district, and use these factors as potential covariates in a statistical model on the quality of educational resources in Massachusetts. Of course, more metrics and qualitative information about school districts and their performance would be needed to perform such assessments.

In order to run the program, you will need to get an API key for Google Maps geocoding and put it into auth.json in the following format:
{"services": {"googlemaps": {"key": <API key>}}}  
  
Additionally, the Shapely and Pyproj libraries are required to convert the school district shapefile coordinates into Latitude/Longitude and to determine whether libraries are within school districts.

Data sources:  
Class sizes: http://profiles.doe.mass.edu/statereport/classsizebyraceethnicity.aspx  
Grade levels: http://profiles.doe.mass.edu/state_report/gradesbydistrict.aspx  
Public libraries: https://publiclibraries.com/state/massachusetts/  

Note: due to issues with the retrieved data sets that I have not yet fixed or found solutions for, the count data in the resulting collections is not always completely accurate (for instance, the libraries per school district count says 0 for some districts that definitely contain libraries).

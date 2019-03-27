# http://www.andymboyle.com/2011/11/02/quick-csv-to-json-parser-in-python/

import csv
import json

# Open the CSV
f = open('data/Voting_Eligible_by_Ward_Boston_Copy.csv')

# Change each fieldname to the appropriate field name
reader = csv.DictReader(f, fieldnames = ("Ward",
                                         "Total",
                                         "Asian",
                                         "Black",
                                         "Hispanic",
                                         "White, non-Hispanic",
                                         "Asian_percentage",
                                         "Black_percentage",
                                         "Hispanic_percentage",
                                         "White, non-Hispanic_percentage"
                                         ))

# Parse the CSV into JSON
out = json.dumps([ row for row in reader ])
print ("JSON parsed!")

# Save the JSON
f = open('Voting_Eligible_by_Ward_Boston_Copy.json', 'w')
f.write(out)
print ("JSON saved!")
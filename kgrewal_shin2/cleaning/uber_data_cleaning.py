# data from https://movement.uber.com/explore/boston/travel-times/query?lang=en-US&si=290&ti=&ag=censustracts&dt[tpb]=ALL_DAY&dt[wd;]=1,2,3,4,5,6,7&dt[dr][sd]=2018-01-01&dt[dr][ed]=2018-02-28&cd=&sa;=-71.0654886,42.3549544&sdn=Boston%20Common,%20139%20Tremont%20St,%20Boston,%20MA&lat.=42.3584308&lng.=-71.1007732&z.=12

import pandas as pd

file_name = 'boston_common_ubers.csv'

sheet = 'boston_common_ubers'

df = pd.read_csv(file_name)
print(df.head(5))


out = df.to_json(orient='records')

with open('boston_common_ubers.json', 'w') as f:
    f.write(out)


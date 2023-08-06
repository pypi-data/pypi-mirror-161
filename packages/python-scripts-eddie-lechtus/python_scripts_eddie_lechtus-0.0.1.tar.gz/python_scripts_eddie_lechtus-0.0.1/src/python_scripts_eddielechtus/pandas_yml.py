import pandas as pd

df = pd.read_csv('/Users/eddielechtus/Ed/docker/get2sailDocker/get2sail_db.csv')
# cell = df.loc[1, 'lat']
# print(cell)
for x in df.index:
    if df.loc[x, 'lat'] > 90:
        df.loc[x, 'lat'] = 30
print(df.to_string())

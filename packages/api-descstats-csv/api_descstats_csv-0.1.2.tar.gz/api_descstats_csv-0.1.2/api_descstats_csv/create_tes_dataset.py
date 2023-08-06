import pandas as pd

df = pd.read_csv(r'data/T1.csv')
df = df.sample(10000)
df.to_csv(r'data/dataset_subset.csv', index=False)

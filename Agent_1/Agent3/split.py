import pandas as pd 
import os 
df = pd.read_csv('./.tranco/top-1m.csv')

df_subset = df.head(150000)

n = 100
folder_1 = 'folder_1'
folder_2 = 'folder_2'
os.makedirs(folder_1, exist_ok=True)
os.makedirs(folder_2, exist_ok=True)


for i in range(0,len(df_subset),n):
    subset = df_subset.iloc[i:i+n]
    if i < 75000: 
        folder = folder_1
    else: 
        folder = folder_2
    subset.to_csv(f"{folder}/{i // n + 1}.csv", index=False)









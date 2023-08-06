import pandas as pd

mydata={'A':1,'B':20}
df=pd.DataFrame([mydata])
print(df.head())
#df_item=pd.read_csv("data/items/items.csv")
#df_item.to_parquet("data/test",engine="fastparquet",compression="gzip",index=False,partition_cols=["CATEGORIES"])
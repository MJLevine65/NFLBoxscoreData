import pandas as pd

def process_snap_data(dataframe : pd.DataFrame) -> pd.DataFrame:
   
    for i, row in dataframe.iterrows():
        dataframe.at[i, "off_pct"] = int(row['off_pct'].replace("%","")) / 100
        dataframe.at[i, "def_pct"] = int(row['def_pct'].replace("%","")) / 100
        dataframe.at[i, "st_pct"] = int(row['st_pct'].replace("%","")) /100

    return dataframe
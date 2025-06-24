import pandas as pd
import sys
import os
with open("bad_rows.txt","w") as f:
    for infile in os.listdir("wyniki"):
        data = pd.read_csv(f"./wyniki/{infile}",header=None)
        data=data.drop(data.axes[-1][-1],axis=1)
        data=data.drop(0,axis=1)
        data_numeric=data.apply(pd.to_numeric, errors='coerce')
        mask=data_numeric>120
        rows_with_true = mask.any(axis=1)
        indices = data.index[rows_with_true]
        rows=data.iloc[indices]
        for i,row in rows.iterrows():
            print(list(row))
            scenario=(f"{row.iloc[0]}{row.iloc[1].lstrip()}{row.iloc[2]},{row.iloc[3]},{row.iloc[4]},{row.iloc[5]}\n")
            f.writelines(scenario)
            print(scenario)

    


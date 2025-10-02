import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1z_L4MEGv5q89OFkuN2RNI1gjajddD3_NG169_f0RNrA/gviz/tq?tqx=out:csv&sheet=ppc_boss"
df = pd.read_csv(url)
row = df[df["slug"] == "ephialtes"].iloc[0]
print(row["knight"])
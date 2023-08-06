import acr_cas_ppi as acp
import pandas as pd

df = pd.read_csv("example.csv")
var = df.to_numpy()
x = acp.predict(var)
print(x)
y = acp.predict_proba(var)
print(y)
acp.gen_file(var)
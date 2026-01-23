import pandas as pd

df = pd.DataFrame({'key': range(6), 'values': list('abcdef')})
df1 = pd.get_dummies(df, drop_first=True)
print(df1)
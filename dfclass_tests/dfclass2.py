import pandas as pd
import numpy as np


index1 = [np.zeros(3, dtype=int),
          np.array([0,1,2])]
index2 = [np.ones(2, dtype=int),
          np.array([0,1])]

df1 = pd.DataFrame(['a1', 'a2', 'a3'])
# df1.columns = ['jets']
df2 = pd.DataFrame(['b1', 'b2'])
# df2.columns = ['subjets']

# print(df1)
# print('---')
# print(df2)
# print('---')

# dfsum1 = df1.append(df2)
dfsum1 = pd.concat([df1, df2], keys=[0, 1])
# print(dfsum1.index)
# print(dfsum1)
# print('---')

# df = df1.append(df2, ignore_index=True)
# print(df)

df3 = pd.DataFrame(['c1', 'c2', 'c3'])
# df1.columns = ['jets']
df4 = pd.DataFrame(['d1', 'd2'])
# df2.columns = ['subjets']

# dfsum2 = df3.append(df4)
dfsum2 = pd.concat([df3, df4], keys=[0, 1])
# dftot = dfsum1.append(dfsum2)
# dfsum1.reset_index(level=0, drop=True, inplace=True)
# dfsum2.reset_index(level=0, drop=True, inplace=True)
dftot = pd.concat([dfsum1, dfsum2], keys=[0, 1])

# print(dfsum2)
print('---')
print(dftot)
print('---')
print(dftot.index)

dftot2 = dftot

# dftot3 = pd.concat([dftot, dftot2])
# dftot.reset_index(level=2, drop=True, inplace=True)
# dftot2.reset_index(level=2, drop=True, inplace=True)
dftot3 = dftot.append(dftot2)
print('---')
print(dftot3)
print('---')
print(dftot3.index)

# index_list = dftot3.index.tolist()
# for t in index_list:
#     t = list(t)
# print(index_list)

dfmulti = dftot3.index.to_frame(index=False)
print('---')
print(dfmulti)

is_first_zero = True
prev_n = 0
shift = 0
for i, row in dfmulti.iterrows():
    n = row[0]
    diff = n - prev_n
    if diff < 0 and not is_first_zero:
        shift += prev_n + 1
    elif diff != 0:
        is_first_zero = False
    dfmulti.at[i, 0] = n + shift
    prev_n = n

print('---')
print(dfmulti)

# for row in dfmulti.itertuples():
#     print(row)



# dfmulti.loc[3] = [6, 6, 6]
# dftot3.index = pd.MultiIndex.from_frame(dfmulti)
# print(dftot3)




import pandas as pd
import numpy as np
import timeit



def combine(dflist):
    df = pd.concat(dflist)
    idf = df.index.to_frame(index=False, name=range(df.index.nlevels))

    is_first_zero = True
    prev_n = 0
    shift = 0
    for i, row in idf.iterrows():
        n = row[0]
        diff = n - prev_n
        if diff < 0 and not is_first_zero:
            shift += prev_n + 1
        elif diff != 0:
            is_first_zero = False
        idf.at[i, 0] = n + shift
        prev_n = n
    mindex = pd.MultiIndex.from_frame(idf)
    df.set_index(mindex, inplace=True)
    
    return df


def combine_fast(dflist):
    shift = 0
    newlist = []

    for df in dflist:
        indexdf = df.index.to_frame(index=False, name=range(df.index.nlevels))
        indexdf[0] += shift
        index = pd.MultiIndex.from_frame(indexdf)
        df.set_index(index, inplace=True)
        newlist.append(df)
        shift += len(set(indexdf[0]))
    dfsum = pd.concat(newlist)

    return dfsum


def combine_2(dflist):
    shift = 0

    for df in dflist:
        df.index.set_levels(df.index.levels[0] + shift, level=0, inplace=True)
        # shift += df.index.to_series().nunique()
        # shift += df.groupby(df.index.names).ngroup
        print(df.groupby(df.index.names).ngroup)
    
    return pd.concat(dflist)



df1 = pd.DataFrame(np.random.randn(2, 1), index=[0, 1])
df2 = pd.DataFrame(np.random.randn(3, 1), index=[0, 1, 2])
dfx = pd.concat([df1, df2], keys=[0, 1])

df3 = pd.DataFrame(np.random.randn(2, 1), index=[0, 1])
df4 = pd.DataFrame(np.random.randn(4, 1), index=[0, 1, 2, 3])
df5 = pd.DataFrame(np.random.randn(3, 1), index=[0, 1, 2])
dfy = pd.concat([df3, df4, df5], keys=[0, 1, 2])

df6 = pd.DataFrame(np.random.randn(3, 1), index=[0, 1, 2])
df7 = pd.DataFrame(np.random.randn(2, 1), index=[0, 1])
dfz = pd.concat([df6, df7], keys=[0, 1])


dfsum1 = pd.concat([dfx, dfy, dfz])
dfsum2 = pd.concat([dfy, dfx])
dfsum3 = pd.concat([dfsum1, dfsum2], keys=[0, 1])
dfsum4 = pd.concat([dfsum2, dfsum1], keys=[0, 1])
dfsum4[0] = 0

# print(b.index)
# print(dfx)
# print(dfy)
# print(dfz)
# print(pd.concat(list))

# a = combine(dflist)
# print(a)
# print(dfsum4.index)
# idf4 = dfsum4.index.to_frame(index=False, name=range(3))
# print(idf4)
# idf4[0] += 33
# print(idf4)
# print(len(set(idf4[0])))
# dfsum5 = combine([dfsum3, dfsum4])
# print(dfsum5.to_string())
# print(dfsum5.index)

start = timeit.default_timer()

# h5file = pd.read_hdf('test.h5')
# h5file_copy = pd.read_hdf('test.h5')
dflist = [dfsum3, dfsum4]
b = combine_2(dflist)
print(b)


# h5sum1 = combine_fast([h5file, h5file_copy])
# print(h5sum1)
# print(h5file)
# print(len(h5file))


end = timeit.default_timer()
print("{:.2f} s".format(end - start))
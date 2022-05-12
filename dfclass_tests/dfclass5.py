import pandas as pd
import numpy as np
import timeit




def combine_1(dflist, level=0):
    shift = 0

    for df in dflist:
        indexdf = df.index.to_frame(index=False, name=range(df.index.nlevels))
        indexdf[level] += shift
        index = pd.MultiIndex.from_frame(indexdf)
        df.set_index(index, inplace=True)
        shift += len(set(indexdf[level]))

    return pd.concat(dflist)

def combine_2(dflist, level=0):
    shift = 0

    for df in dflist:
        df.index.set_levels(df.index.levels[level] + shift, level=level, inplace=True)
        shift += df.index.levshape[level]
        print(df.index.levshape)
        # shift += df.groupby(df.index.names).ngroups
        # print(df.index.to_series())

    return pd.concat(dflist)




# shift += df.index.to_series().nunique()
# print(df.index.to_series())
# shift += df.groupby(df.index.names).ngroups
# print(df.groupby(df.index.names).ngroup)
# print(df.index.levshape[0])



h5file = pd.read_hdf('test.h5') # -> each with 3682 events
h5file_copy = pd.read_hdf('test.h5')


# print(h5file.index.to_series().nunique())


start = timeit.default_timer()


h5sum = combine_2([h5file, h5file_copy])









end = timeit.default_timer()

print(h5sum)
print("{:.0f} ms".format(1000*(end - start)))
import pandas as pd
import timeit

def combine(dflist, level=0):
    shift = 0

    for df in dflist:
        df.index.set_levels(df.index.levels[level] + shift, level=level, inplace=True)
        shift += df.index.levshape[level]

    return pd.concat(dflist)



l = 28 # 280 = ~1M events
dflist = [0]*l
for i in range(l):
    dflist[i] = pd.read_hdf('test.h5') # = 3682 events
    print("reading df file: {}".format(i))

m = 50
sumlist = [0]*m
for i in range(m):
    sumlist[i] = combine(dflist)
    print("combining dfs: {}".format(i))


start = timeit.default_timer()


print(combine(sumlist))


end = timeit.default_timer()
print("{:.0f} s".format((end - start)))

"""
Each df is 1M events

115 sec for 5 dfs
(tried 10 dfs -> code killed due to 
too much memory consumption)

-> try combining 100 df of 100k events each
(might not kill memmory)
result (10M events) = Killed

-> try combining 50 dfs
result (10M events) = 172 sec (with printing)
                    = 137 sec (without printing)
But was measuring the creation of dataframes...
result = 87 +/- 7 sec (10 measurements)
"""





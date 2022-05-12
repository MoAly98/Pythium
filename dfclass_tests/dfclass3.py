import pandas as pd
import numpy as np


class PythiumDF():

    def __init__(self, pd_dataframe):
        self.df = pd_dataframe
        self.n_events = pd_dataframe.index.levshape[0]
        self.list_columns = pd_dataframe.columns
        
	# function to merge multiple dfs preserving multi-indexing
    def combine(dflist):
        shift = 0
        for df in dflist:
            df.index.set_levels(df.index.levels[0] + shift, level=0, inplace=True)
            shift += df.index.levshape[0]
        return PythiumDF(pd.concat(dflist))
    
    # printing functions
    def __repr__(self):
        return "PythiumDF()"
    def __str__(self):
        return "\n --- \n" + self.df.__str__() + "\n --- \n"


df1 = pd.read_hdf("test.h5")
df2 = pd.read_hdf("test.h5")

obj = PythiumDF.combine([df1, df2])

print(obj)
print(obj.list_columns)
print(obj.n_events)
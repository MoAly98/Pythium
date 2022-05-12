import pandas as pd


class PythiumDF():

    def __init__(self, pandas_df):
        self.pythium_df = pandas_df

    def get_pandas(self):
        return self.pythium_df

    def combine(self, dflist): # dflist must contain Pythium dfs

        local_list = []
        local_list.append(self.get_pandas())
        shift = self.get_pandas().index.levshape[0]

        for df in dflist:
            df.get_pandas().index.set_levels(df.get_pandas().index.levels[0] + shift, level=0, inplace=True)
            shift += df.get_pandas().index.levshape[0]
            local_list.append(df.get_pandas())

        self.pythium_df = pd.concat(local_list)

    ## combine() can become a static method

    # printing functions
    def __repr__(self):
        return "PythiumDF()"
    def __str__(self):
        return "\n --- \n" + self.get_pandas().__str__() + "\n --- \n"


obj1 = PythiumDF(pd.read_hdf("test.h5"))
obj2 = PythiumDF(pd.read_hdf("test.h5"))
obj3 = PythiumDF(pd.read_hdf("test.h5"))

objlist = [obj2, obj3]
print(obj1)
obj1.combine(objlist)

print(obj1)
print(type(obj1))
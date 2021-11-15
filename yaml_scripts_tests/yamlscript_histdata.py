import yaml
import pandas as pd

if __name__ == '__main__':

    stream = open("CR_ttb_prefit.yaml", "r")
    dictionary = yaml.full_load(stream)
    print(type(dictionary))

    dfdict = {}
    for key, value in dictionary.items():
        dfdict["df_{0}".format(key)] = pd.DataFrame(dictionary[key])

    samples = dfdict['df_Samples']
    yield_df = pd.DataFrame(samples['Yield'].to_list(), columns=[f"Yield_{i}" for i in range(len(samples.loc[0][1]))])
    samples = pd.concat([samples, yield_df], axis=1).drop('Yield', axis=1)
    print(samples)

    total = dfdict['df_Total']
    # print(total)
    data = dfdict['df_Data']
    # print(data)
    figure = dfdict['df_Figure']
    # print(figure)

    # print(type(total))
    # df = pd.DataFrame(total.loc[0][0])
    # print(df)
    def df_fixer(df):

        col_dfs = []
        for i in range(len(df.loc[0,:])):
            col_name = df.columns[i]
            newdf = pd.DataFrame(df.iloc[0][i], columns=[col_name])
            col_dfs.append(newdf)
        
        return pd.concat(col_dfs, axis=1)

    total_fixed = df_fixer(total)
    print(total_fixed)
    data_fixed = df_fixer(data)
    print(data_fixed)
    # figure_fixed = df_fixer(figure)
    # print(figure_fixed)
    # print(type(figure.to_dict()['BinEdges']))

    def df_from_key(df, key):
        return pd.DataFrame(df.to_dict()[key]).rename(columns={0:key})

    bin_edges_df = df_from_key(figure, 'BinEdges')
    print(bin_edges_df)


    




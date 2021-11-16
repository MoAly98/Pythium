import yaml
import pandas as pd

if __name__ == '__main__':

    # this function takes a 1x3 df where each cell is a list of values
    # that would be much more easily visible in a column format
    def df_fixer(df):

        col_dfs = []
        for i in range(len(df.loc[0,:])):
            col_name = df.columns[i]
            newdf = pd.DataFrame(df.iloc[0][i], columns=[col_name])
            col_dfs.append(newdf)
        
        return pd.concat(col_dfs, axis=1)

    # parse yaml structure
    file_name = "CR_ttb_prefit.yaml"
    stream = open(file_name, "r")
    dictionary = yaml.full_load(stream)

    # transform each element (sample, total, data, figure) of dictionary
    # into readable dataframes (where convenient)
    samples = pd.DataFrame(dictionary['Samples'])
    # expand each row (which is a list) into separate columns
    # for each element
    yield_df = pd.DataFrame(samples['Yield'].to_list(), columns=[f"Yield_{i}" for i in range(len(samples.loc[0][1]))])
    samples = pd.concat([samples, yield_df], axis=1).drop('Yield', axis=1)

    total = pd.DataFrame(dictionary['Total'])
    total_fixed = df_fixer(pd.DataFrame(total))

    data = pd.DataFrame(dictionary['Data'])
    data_fixed = df_fixer(pd.DataFrame(data))

    dictionary['Samples'] = samples
    dictionary['Total'] = total_fixed
    dictionary['Data'] = data_fixed

    print(dictionary)


    




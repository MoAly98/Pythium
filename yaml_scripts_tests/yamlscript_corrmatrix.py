import yaml
import pandas as pd

if __name__ == '__main__':

    stream = open("CorrelationMatrix.yaml", 'r')
    dictionaries = yaml.full_load(stream)
    dflist = []
    for dict in dictionaries:
        df = pd.DataFrame(dict)
        dflist.append(df)
        # print(df)

    # print(dflist[1].loc[0][0])
    parameters_df = dflist[0]
    matrix_df = dflist[1]
    matrix_df = pd.DataFrame(matrix_df['correlation_rows'].to_list(), columns=range(len(matrix_df)))

    print(parameters_df)
    print(matrix_df)
    
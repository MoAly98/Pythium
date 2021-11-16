from numpy.matrixlib.defmatrix import matrix
import yaml
import pandas as pd

if __name__ == '__main__':

    # parse yaml structure
    stream = open("CorrelationMatrix.yaml", 'r')
    dictionaries = yaml.full_load(stream)

    # create list containing parameters df and matrix df
    dflist = []
    for dict in dictionaries:
        df = pd.DataFrame(dict)
        dflist.append(df)

    parameters_df = dflist[0]
    matrix_df = dflist[1]
    # expand each row (which is a list) into separate columns
    # for each element
    matrix_df = pd.DataFrame(matrix_df['correlation_rows'].to_list(), columns=range(len(matrix_df)))

    serie = parameters_df['parameters']
    # change row names
    matrix_df.set_index(serie, inplace=True)
    # change column names
    matrix_df.rename(columns=serie, inplace=True)
    print(matrix_df)
    
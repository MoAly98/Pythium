import yaml
import pandas as pd


def corrmatrix_parser(file_name):

    with open(file_name, "r") as stream:
        list_dict = yaml.full_load(stream) # this is a list of dictionaries (for some reason...)

        # convert dictionaries into dfs
        parameters_df = pd.DataFrame(list_dict[0])
        matrix_df = pd.DataFrame(list_dict[1])
        # expand each row (which is a list) into separate columns for each element
        matrix_df = pd.DataFrame(matrix_df['correlation_rows'].to_list(), columns=range(len(matrix_df)))

        serie = parameters_df['parameters'] # take 'parameters' serie object
        matrix_df.set_index(serie, inplace=True) # change row names
        matrix_df.rename(columns=serie, inplace=True) # change column names

        return matrix_df


if __name__ == "__main__":
    corrmatrix_parser("CorrelationMatrix.yaml")
        
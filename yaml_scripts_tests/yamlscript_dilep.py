import yaml
import pandas as pd


def dilep_parser(file_name):

    with open(file_name, "r") as stream:
        list_dict = yaml.full_load(stream)

    fixed_list = [] # list to store fixed dfs
    regions = []
    for dict in list_dict:
        df = pd.DataFrame(dict) # convert dictionary into df

        # fix last dictionary on 'Sampels' column (the 'Data' entry)
        cell_to_fix = df.iloc[-1][1] # cell_to_fix is a dictionary
        cell_to_fix['Sample'] = cell_to_fix.pop('Data')
        df.iloc[-1][1] = cell_to_fix

        # expand dictionaries into columns with .json_normalize
        correct_df = pd.json_normalize(df['Samples'])

        # horizonthally attach expanded df and drop old column
        result = pd.concat([df, correct_df], axis=1).drop('Samples', axis=1)
        fixed_list.append(result)
        regions.append(result.iloc[0][0])

    # put together all fixed dfs
    merged = pd.concat(fixed_list, keys=regions).drop(columns='Region')
    
    return merged


if __name__ == "__main__":
    dilep_parser("tables_dilep.yaml")


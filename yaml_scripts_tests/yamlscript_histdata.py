import yaml
import pandas as pd
import matplotlib.pyplot as plt


def histdata_parser(file_name):

    with open(file_name, "r") as stream:
        dictionary = yaml.full_load(stream)

        # convert dictionaries into dfs
        samples_df = pd.DataFrame(dictionary['Samples'])
        total_df = pd.DataFrame(dictionary['Total']).T
        data_df = pd.DataFrame(dictionary['Data']).T
        figure_df = pd.DataFrame(dictionary['Figure']).T

        samples_df.set_index('Name', inplace=True)
        # set column name of total_df and data_df to 'Yield' to match samples_df
        total_df.rename(columns={0:'Yield'}, inplace=True)
        data_df.rename(columns={0:'Yield'}, inplace=True)

        # merge them with multi-indexing
        sum = pd.concat([samples_df, total_df, data_df], keys=['Samples', 'Total', 'Data'])
        # at this point, rows in sum are list of 10 numbers, each corresponding
        # to a different yield -> need to split them and put them into individual columns
        
        temp_df = pd.DataFrame(sum['Yield'].to_list(), columns=[f"Yield_{i}" for i in range(len(sum.iloc[0][0]))])
        # match index of temp_df and sum to allow concat later
        temp_df.set_index(sum.index, inplace=True)
        sum = pd.concat([sum, temp_df], axis=1).drop('Yield', axis=1)
        
        print(sum)
        print(figure_df)

        # nbins = 10
        # fig, ax = plt.subplots()
        # sum.plot.hist(bins=nbins)


if __name__ == "__main__":
    histdata_parser("CR_ttc_prefit.yaml")
    # file1 = "CR_ttc_prefit.yaml"
    # file2 = "CR_ttb_prefit.yaml"

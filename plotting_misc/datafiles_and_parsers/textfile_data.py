import pandas as pd


def txt_parser(file_name):

    with open(file_name) as file:
        dict = {}
        for i, line in enumerate(file):
            splitted = line.split()
            if len(splitted) == 4: # discard corr matrix part of file
                dict[i] = splitted
        
        df = pd.DataFrame(dict).T
        # set first column ("parameters") as index of df
        df.set_index(0, inplace=True)

    return df


if __name__ == "__main__":
    txt_parser("tHbb_v31_v3.txt")


import pandas as pd

file_name = "tHbb_v31_v3.txt"

with open(file_name) as file:

    dict = {}
    i = 0
    for line in file:
        splitted = line.split()
        if len(splitted) == 4: # discard corr matrix part of file
            # print(splitted)
            dict[i] = splitted
            i += 1
    df = pd.DataFrame(dict).T
    # set first column (parameters) as index of df
    df.set_index(0, inplace=True)

    # print(df)
        





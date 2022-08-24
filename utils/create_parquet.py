import awkward as ak
import numpy as np
import os 

akarr = ak.Array({'observable1': np.arange(10), 'observable2': np.arange(10)*10})
os.makedirs(f'{os.getcwd()}/tests/histogramming/data/', exist_ok=True)
ak.to_parquet(akarr, f'{os.getcwd()}/tests/histogramming/data/sample_tree1.parquet')
ak.to_parquet(akarr, f'{os.getcwd()}/tests/histogramming/data/sample_tree2.parquet')
ak.to_parquet(akarr, f'{os.getcwd()}/tests/histogramming/data/sample2_tree1.parquet')
ak.to_parquet(akarr, f'{os.getcwd()}/tests/histogramming/data/sample2_tree2.parquet')

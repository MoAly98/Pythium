import awkward as ak
import numpy as np
import os 
test_data_dir = os.path.dirname(os.path.abspath(__file__))

akarr = ak.Array({'observable1': np.arange(10), 'observable2': np.arange(10)*10})
ak.to_parquet(akarr, f'{test_data_dir}/sample_tree.parquet')
ak.to_parquet(akarr, f'{test_data_dir}/sample_tree2.parquet')


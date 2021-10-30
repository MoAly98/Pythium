from slimming_proto_config import sample_list
from example_slimming_config import sample_list
from common_tools import branch_expr_to_df_expr
from argparse import ArgumentParser, ArgumentTypeError
import uproot4 as uproot
import awkward1 as ak
import pandas as pd
import time

import preprocess as proc

#preprocess.run()


print('test')
for sample in sample_list:
		for ntuple_args in sample.get_uproot_args():
			t1 = time.time()
			slimmed_df = proc.slimit(ntuple_args)
			t2 = time.time()
			print("Slimming time:", t2-t1)
			slimmed_df.to_hdf('Skl_Data/test.h5', key='branches')
			t3 = time.time()
			print("Dumping time:", t3-t2)
			df_from_hdf = pd.read_hdf('Skl_Data/test.h5', key='branches')
			t4 = time.time()
			print("Re-reading time:", t4-t3)
			# If user dropping branches, will get back a list of dfs to avoid
			# indexing problems
			if(isinstance(slimmed_df, dict)):
				# Do some sort of COMBO of individual branch dataframes
				pass
			else:
				print('byebye')


import storage_functions as sf
import hist_vars


var_dict = sf.combine_dicts([hist_vars.var_main, hist_vars.var_series, hist_vars.var_beta, 
                               hist_vars.var_ecf_beta, hist_vars.var_dichoric, hist_vars.var_ecfg])

client_params = {
    "n_workers" : 4,
    "memory_limit" : '5GB',
    "threads_per_worker" : 1
}

file_list = {
    "top_directory" : '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_SEP_v2/',
    "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
}

computation_params = {
    "chunk_size" : 100, 
    "histogram_variables" : var_dict
}

out_dir = '/tmp/kmalirz'

from pathlib import Path
from utils.histogramming.TaskManager import _TaskManager
from utils.histogramming.objects import Observable, _Binning, _Systematic, NTupSyst, TreeSyst, CrossProduct
from utils.common.functor import Functor
from glob import glob 
import os
from collections import defaultdict
from pprint import pprint
import dask
import boost_histogram as bh

class Processor(object):    
    def __init__(self, config):
        self.cfg = config

    def get_input_files(self, sample, observable, systematic, template,):
        indirs = self.cfg["general"]["indir"]
        from_pyth = self.cfg["general"]["frompythium"]
        ext = self.cfg["general"]["informat"]

    def create(self):
        #======= Output location of histogram
        hist_folder = Path(self.cfg["general"]["outdir"])
        os.makedirs(hist_folder, exist_ok=True)
        #======= Analysis objects from config 
        samples =  self.cfg["samples"]
        regions = self.cfg["regions"]
        systematics = self.cfg["systematics"]
        observables = self.cfg["observables"]

        
        xp_iter = list(self.cross_product(samples, regions, systematics, observables))
        input_manager =  InputManager(xp_iter, self.cfg)
        xp_to_req_vars = input_manager.required_variables()
        xp_to_paths = input_manager.required_paths()

        task_manager = _TaskManager(hist_folder, input_manager.reader)
        task_tree= task_manager._build_tree(xp_to_paths, xp_to_req_vars)
        histograms = dask.compute(*task_tree, scheduler = "synchronous")

    
    def cross_product(self, samples, regions, systematics, observables):
        for sample in samples:
            for region in regions:
                for obs in observables:
                    for syst in [None]+systematics:
                        templates: List[Literal["nom", "up", "down"]]
                        if syst is None:    templates = ['nom']
                        else:   templates = ["up","down"]
                        for template in templates:                            
                            h_wanted = _TaskManager.hist_wanted(sample, region, obs, syst, template)
                            if not h_wanted:    continue   
                            
                            yield CrossProduct(sample, region, obs, syst, template,)
    
class InputManager(object):
    def __init__(self, xps, cfg):
        read_methods = {
                        'parquet': 'ak_parquet',
                        'json': 'ak_json',
                        'root': 'uproot',
                        'h5': 'ak_h5'
                        }
        self.xps = xps
        self.indirs = cfg["general"]["indir"]
        self.from_pyth = cfg["general"]["frompythium"]
        self.ext = cfg["general"]["informat"]
        self.sample_sel = cfg["general"]["samplesel"]
        self.reader = read_methods[self.ext]
    
    def required_variables(self):
        req_vars: List[Observable] = []
        xp_to_req = defaultdict(list)
        for xp in self.xps:
            sample, region, obs, syst, template = xp
            required_variables = []
            obs_vars, _region_sel_vars, sample_sel_vars, syst_vars = [],[],[],[]
            
            if obs.builder is None:   obs_vars = [obs]
            else:
                obs_vars = [Observable(reqvar, reqvar, obs.binning, obs.dataset) for reqvar in obs.builder.req_vars ]

            region_sel_vars =  [ Observable(reqvar, reqvar, obs.binning, obs.dataset) for reqvar in region.sel.req_vars ] 
            if self.sample_sel:
                sample_sel_vars =  [ Observable(reqvar, reqvar, obs.binning, obs.dataset) for reqvar in sample.sel.req_vars ]
            
            if isinstance(systematic, WeightSyst):
                template = getattr(systematic, template)
                if isinstance(template, Functor):
                    syst_vars =  [ Observable(reqvar, reqvar, obs.binning, obs.dataset) for reqvar in template.req_vars ] 
                else:
                    syst_vars = [Observable(template, template, obs.binning, obs.dataset)]  
            
            required_variables.extend([ obs_vars, region_sel_vars, sample_sel_vars, syst_vars])
            
            xp_to_req[xp] = required_variables
            
        return xp_to_req

    def required_paths(self):
        xp_to_paths = defaultdict(list)
        for xp in self.xps:
            sample, region, observable, systematic, template = xp
            if self.from_pyth:  # Follow pythium naming scheme
                sample_name = sample.name
                obs_dataset = observable.dataset
                paths = [f"{path}/{sample_name}_*_{obs_dataset}.{self.ext}" for path in self.indirs]
                if template != 'nom':
                    if isinstance(systematic, NTupSyst):
                        sys_dirs =    getattr(systematic, "where")
                        sys_samples = getattr(systematic, template)
                        if sys_dirs == [None]:
                            paths = [f"{indir}/{s_samp}_*_{obs_dataset}.{self.ext}" for indir in indirs for s_samp in sys_samples]
                        else:
                            paths = [f"{s_dir}/{s_samp}_*_{obs_dataset}.{self.ext}" for s_dir in sys_dirs for s_samp in sys_samples]
                    elif (isinstance(systematic, TreeSyst)):
                        syst_dataset = getattr(systematic, template) 
                        paths = [f"{indir}/{sample_name}_*_{syst_dataset}.{self.ext}" for indir in self.indirs]

                paths = list(set([p for path in paths for p in glob(path) if not os.path.isdir(p) ]))
                xp_to_paths[xp] = paths
               
            
            else:
                ## TODO:: Assume user defined (somehow?) #Custom? some supported special types? decoreator for custom?
                logger.warning("Only outputs from Pythium currently supported")
                pass

        return xp_to_paths
            
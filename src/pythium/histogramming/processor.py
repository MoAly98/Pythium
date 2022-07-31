from pathlib import Path
from pythium.histogramming.managers import _TaskManager, _InputManager
from pythium.histogramming.objects  import Observable, NTupSyst, TreeSyst, WeightSyst, CrossProduct
from pythium.histogramming.binning import _Binning
from pythium.common.functor import Functor
from pythium.common.logger import ColoredLogger
import os
from collections import defaultdict
from pprint import pprint
import dask
import boost_histogram as bh
import pickle

class Processor(object):    
    
    
    def __init__(self, config, scheduler):
        self.cfg = config
        self.outdir = Path(self.cfg["general"]["outdir"])
        os.makedirs(self.outdir, exist_ok=True)
        self.scheduler = scheduler
        self.graph = None
        self.xps = None
    
    def get_input_files(self, sample, observable, systematic, template,):
        indirs = self.cfg["general"]["indir"]
        from_pyth = self.cfg["general"]["frompythium"]
        ext = self.cfg["general"]["informat"]

    def create(self):
        logger = ColoredLogger()
        #======= Analysis objects from config 
        samples =  self.cfg["samples"]
        regions = self.cfg["regions"]
        systematics = self.cfg["systematics"]
        observables = self.cfg["observables"]

        
        xp_iter = list(self.cross_product(samples, regions, systematics, observables))
        input_manager =  _InputManager(xp_iter, self.cfg)
        xp_to_req_vars = input_manager.required_variables()
        xp_to_paths = input_manager.required_paths()
        task_manager = _TaskManager(input_manager.reader, sample_sel = self.cfg["general"]["samplesel"])
        
        task_tree, xps = task_manager._build_tree(xp_to_paths, xp_to_req_vars)
        dask.visualize(task_tree, filename=f'{self.outdir}/task_graph.png')
        
        self.graph = task_tree
        logger.info(f"Number of histograms to produce is {len(self.graph)}")
        self.xps = xps

    def run(self):
        
        
        histograms = dask.compute(*self.graph, scheduler = self.scheduler)
        dd = defaultdict(dict)
        for i, xp in enumerate(self.xps):
            sample, region, obs, syst, template = xp
            if syst is not None:
                dd[obs.name].update({f'{sample.name}_{region.name}_{syst.name}_{template}': histograms[i]})
            else:
                dd[obs.name].update({f'{sample.name}_{region.name}_{template}': histograms[i]})
        return dd

    def save(self, hists_dict):
        for obs in list(hists_dict.keys()):
            fname = f'{obs}.pkl'
            with open(f"{self.outdir}/{fname}", "wb") as f:
                pickle.dump(hists_dict[obs], f)


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
    

            
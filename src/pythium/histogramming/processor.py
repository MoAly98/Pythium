'''
This is where that steers that handles that booking-keeping for histogramming tasks
'''
# Python imports
from pathlib import Path
import os
import pickle
from collections import defaultdict
# Scikit-HEP
import dask
# Pythium
from pythium.histogramming.managers import _TaskManager, _InputManager
from pythium.histogramming.objects  import  CrossProduct
from pythium.common.logger import ColoredLogger


class Processor(object):
    '''
    Class which sorts through the user configuration and makes transactions
    with the managers in order to run a histogramming chain
    '''
    def __init__(self, config, scheduler):
        '''
        Attributes:
            config (Dict):  Mapping of the settings from the config file
            scheduler (str):    The scheduler to-be-used by dask
        '''

        self.cfg = config
        self.outdir = Path(self.cfg["general"]["outdir"])
        os.makedirs(self.outdir, exist_ok=True)
        self.scheduler = scheduler
        self.graph = None
        self.xps = None

    def create(self):
        '''
        High-level function through which the user can start the constrction
        of the histogramming task-graph. No computation happens at this point
        '''

        logger = ColoredLogger()

        #======= Analysis objects from config 
        samples =  self.cfg["samples"]
        regions = self.cfg["regions"]
        systematics = self.cfg["systematics"]
        observables = self.cfg["observables"]

        # Build the list of XPs to be computed 
        xp_iter = list(self.cross_product(samples, regions, systematics, observables))
        # Initialize an inputs manager to handle what is needed from inputs
        input_manager =  _InputManager(xp_iter, self.cfg)
        xp_to_req_vars = input_manager.required_variables()
        xp_to_paths = input_manager.required_paths()
        # Intitalise a task manager to handle how the task graph should look
        task_manager = _TaskManager(input_manager.reader, sample_sel = self.cfg["general"]["samplesel"])
        task_tree, xps = task_manager._build_tree(xp_to_paths, xp_to_req_vars)
        # Save the task graph for the user
        dask.visualize(task_tree, filename=f'{self.outdir}/task_graph.png')
        
        self.graph = task_tree
        logger.info(f"Number of histograms to produce is {len(self.graph)}")
        self.xps = xps

    def run(self):
        '''
        Method to compute the histograms
        '''
        # Return a list of histograms, elements correspond to XPs
        histograms = dask.compute(*self.graph, scheduler = self.scheduler)
        
        # Map observables to XP to histograms
        dd = defaultdict(dict)
        for i, xp in enumerate(self.xps):
            sample, region, obs, syst, template = xp
            if syst is not None:
                dd[obs.name].update({f'{sample.name}_{region.name}_{syst.name}_{template}': histograms[i]})
            else:
                dd[obs.name].update({f'{sample.name}_{region.name}_{template}': histograms[i]})
        return dd

    def save(self, hists_dict):
        '''
        Method to save the histograms into output pickle files
        Args:
            hists_dict (Dict): Mapping of observable -> sample_region_syst_template -> histogram
        '''

        for obs in list(hists_dict.keys()):
            fname = f'{obs}.pkl'
            with open(f"{self.outdir}/{fname}", "wb") as f:
                pickle.dump(hists_dict[obs], f)

    def cross_product(self, samples, regions, systematics, observables):
        '''
        Make all cross-products from the user-provided configurations, skipping
        cross-products that aren't needed. 
        '''
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

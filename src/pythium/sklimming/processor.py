from pathlib import Path
import os
class Processor(object):    
    
    def __init__(self, config, scheduler):
        self.cfg = config
        self.outdir = Path(self.cfg["general"]["outdir"])
        os.makedirs(self.outdir, exist_ok=True)
        self.scheduler = scheduler
        self.graph = None
        self.xps = None
    

    def create(self):
        logger = ColoredLogger()
        #======= Analysis objects from config 
        samples =  self.cfg["samples"]
        
        xps = list(self.cross_product())
        input_manager =  _InputManager(self.cfg, xps)
        xp_to_req_vars = input_manager.required_variables()
        xp_to_paths = input_manager.required_paths()
        task_manager = _TaskManager(input_manager.reader, sample_sel = self.cfg["general"]["samplesel"])
        
        task_tree, xps = task_manager._build_tree(xp_to_paths, xp_to_req_vars)
        dask.visualize(task_tree, filename=f'{self.outdir}/task_graph.png')
        
        self.graph = task_tree
        logger.info(f"Number of histograms to produce is {len(self.graph)}")
        self.xps = xps

    def cross_product(self):
        '''
        This function is supposed to build every sample-dataset pair needed
        so that we can extract variables from the relevant file
        '''  
        samples =  self.cfg["samples"]
        for sample in samples:
            datasets = list(set([ds for var in sample.variables for ds in var.datasets]))
            for ds in datasets: yield sample, ds

        
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
    

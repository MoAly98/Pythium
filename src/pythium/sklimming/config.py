from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydoc import importfile
from pythium.common.logger import ColoredLogger
from pythium.common.tools import PythiumList
from pythium.common.objects import Sample
#from pythium.histogramming.objects import *
import os
from schema import Schema, And, Use, Optional, SchemaError, Regex

logger = ColoredLogger()

class Config(object):
    def __init__(self, cfg: Union[Path, str]):
        
        self._cfg_path = str(cfg)

        supported_outputs = ['h5', 'parquet','json']
        supported_inputs = ['root']
        
        def unique_names(x) : return len(set([y.name for y in x])) == len([y.name for y in x])
        def supported_outformat(x): return x in supported_outputs
        def supported_informat(x): return x in supported_inputs
        
        cfg_schema = {
            'samples': And([Sample], lambda x: len(x)>0, unique_names),
            'general': {
                        'indir': And(Use(lambda x: [x] if not isinstance(x, list) else x), [str]),
                        'outdir': Use(str),
                        'outformat': And(str, supported_outformat),
                        Optional('informat', default = 'root'): And(str, supported_informat),
                        Optional('skipmissingfiles', default = False): bool, 
                        Optional('dask', default = False): bool,
                        Optional('dasksettings', default = {'n_workers':3,
                                                            'memory_limit': '3GB',
                                                            'threads_per_worker':3 }): 
                                                            {
                                                                Optional('n_workers', default=3): Use(int) ,
                                                                Optional('memory_limit', default = '3GB'): And(Use(str), Regex(f'[0-9]+(GB|MB|KB|B)')),
                                                                Optional('threads_per_worker', default = 3): Use(int),
                                                            },
                        }
            }

        self.schema = Schema(cfg_schema)


    def process(self, args = None) -> Dict:
        path = self._cfg_path
        cfg_module = importfile(path)
        self.make_dict(cfg_module)
        if args is not None:    self.update(args)
        self.validate()
        return self.cfg
    
    def make_dict(self, module):
        '''
        Write the information from python module to a dict of configs
        '''
        cfg = {}

        cfg['samples'] = getattr(module, "samples", [])
        cfg['general'] = {k.lower(): v for k, v in module.general.items()}

        self.cfg = cfg

    def update(self, args):

        analysis_objects = ['samples']
        for arg in vars(args):
            override = getattr(args, arg)
            
            if override is None:    continue
            
            if arg in analysis_objects:
                if override.lower() == 'none':  self.cfg[arg] = []
                else:   self.cfg[arg] = [obj for obj in self.cfg[arg] if obj.name in override]
            
            elif arg in ['exclude']:
                for objtype in analysis_objects:
                    self.cfg[objtype] = [obj for obj in self.cfg[objtype] if obj.name not in override]
                    if objtype == 'sample':
                        samples = PythiumList(self.cfg[objtype])
                        vars_keep = [ var for var in samples.variables if var.name not in override ]
                        samples.update("variables", vars_keep)
                            
                        
    
    def validate(self):
        valid = self.schema.is_valid(self.cfg)
        valid &= all([var.datasets is not None for sample in self.cfg["samples"] for var in sample.variables ])
        
        if not valid:
            try:
                self.cfg = self.schema.validate(self.cfg)
            except SchemaError as err:
                logger.error(str(err))

            logger.error("All variables declared must have datasets")

        else:
            logger.info("Configuration file is validated")
            self.cfg = self.schema.validate(self.cfg)        

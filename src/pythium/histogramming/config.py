from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydoc import importfile
from pythium.common.logger import ColoredLogger
from pythium.common.samples import Sample
from pythium.histogramming.objects import *
import os
from schema import Schema, And, Use, Optional, SchemaError, Regex

logger = ColoredLogger()

class Config(object):
    def __init__(self, cfg: Union[Path, str]):
        
        self._cfg_path = str(cfg)

        supported_inputs = ['h5', 'parquet','json']
        def unique_names(x) : return len(set([y.name for y in x])) == len([y.name for y in x])
        def supported_informat(x): return x in supported_inputs
        
        cfg_schema = {
            'samples': And([Sample], lambda x: len(x)>0, unique_names),
            'observables': And([Observable], lambda x: len(x)>0, unique_names),
            'regions': And([Region], lambda x: len(x)>0, unique_names),
            Optional('systematics', default = []): [Systematic],
            'general': {
                        'indir': And(Use(lambda x: [x] if not isinstance(x, list) else x), [str]),
                        'outdir': Use(str),
                        'informat': And(str, supported_informat),
                        Optional('samplesel', default = False): bool, 
                        Optional('dask', default = False): bool,
                        Optional('frompythium', default = True): bool,
                        Optional('sklimconfig', default = None): Use(str),
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


    def process(self, args) -> Dict:
        path = self._cfg_path
        cfg_module = importfile(path)
        self.make_dict(cfg_module)
        self.update(args)
        self.validate()
        return self.cfg
    
    def make_dict(self, module):
        '''
        Write the information from python module to a dict of configs
        '''
        cfg = {}

        cfg['samples'] = getattr(module, "samples", [])
        cfg['regions'] = getattr(module, "regions", [])
        cfg['observables'] = getattr(module, "observables", [])
        cfg['systematics'] = getattr(module, "systematics", [])
        cfg['general'] = {k.lower(): v for k, v in module.general.items()}

        if cfg['samples'] == [] and 'sklimconfig' in cfg['general']:
            cfg['samples'] = getattr(importfile(cfg['general']['sklimconfig']), "samples", []) 
        
        self.cfg = cfg

    def update(self, args):

        analysis_objects = ['samples', 'observables', 'regions', 'systematics']
        for arg in vars(args):
            override = getattr(args, arg)
            
            if override is None:    continue
            
            if arg in analysis_objects:
                if override.lower() == 'none':  self.cfg[arg] = []
                else:   self.cfg[arg] = [obj for obj in self.cfg[arg] if obj.name in override]
            
            elif arg in ['exclude']:
                for objtype in analysis_objects:
                    self.cfg[objtype] = [obj for obj in self.cfg[objtype] if obj.name not in override]
            
            elif arg in ['sklimconfig']:
                self.cfg['general']['sklimconfig'] = override

    
    def validate(self):
        valid = self.schema.is_valid(self.cfg)
        if not valid:
            try:    self.cfg = self.schema.validate(self.cfg)
            except SchemaError as err:
                logger.error(str(err))
        else:
            logger.info("Configuration file is validated")
            self.cfg = self.schema.validate(self.cfg)        

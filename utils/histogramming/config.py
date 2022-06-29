from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydoc import importfile

class Config(object):
    def __init__(self, cfg: Union[Path, str]):
        self._cfg_path = str(cfg)
    
    def process(self) -> Dict:
        path = self._cfg_path
        cfg_module = importfile(path)
        self.cfg = self.dump(cfg_module)
        return self.cfg
    def dump(self, module):
        '''
        Write the information from python module to a dict of configs
        '''
        cfg = {}
        cfg['samples'] = module.samples
        cfg['regions'] = module.regions
        cfg['systematics'] = module.systematics
        cfg['observables'] = module.observables
        cfg['general'] = {k.lower(): v for k, v in module.general.items()}
        if not isinstance(cfg['general']['indir'], list):
            cfg['general']['indir'] = [cfg['general']['indir']]
        if 'samplesel' not in cfg['general']:
            cfg['general']['samplesel'] = False
        
        # cfg['client_params'] = parse_client_params(module)
        # cfg['file_list'] = parse_file_list(module)
        # cfg['computation_params'] = parse_computation_params(module)
        # cfg['out_dir'] = module.out_dir
        # cfg['sklim_config'] = module.sklim_config_path

        return cfg
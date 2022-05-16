from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from utils.histogramming.cross_product_backend import XP_Systematics, XP_Sample
from utils.common import logger
from utils.sklimming.config import validate_samples as sklim_validate_samples
from pydoc import importfile
import types
import re, os
logger = logger.ColoredLogger()

def process(cfg_path: Union[str, Path], skl_cfg = None) -> Union[Dict[str, Any], None]:
    '''
    Function to read in a python module and dump the information from
    there into a dictionary.
    If skl_cfg is provided, update the config file at cfg_path.
    Args:
        cfg_path: The path to the configuration file
        skl_cfg: Path to the sklimming configuration file
    Returns:
        config: The dictionary holding information from config file
    '''
    path = str(cfg_path)
    if skl_cfg:
        if not os.path.isfile(skl_cfg):
            logger.error(f'Sklimming configuration file {skl_cfg} does not exist.')
        with open(path,'r') as hist_cfg:
            cfg_data = hist_cfg.read()
        cfg_data = re.sub(r"(sklim_config_path =).*", r"\1 '%s'" % skl_cfg, cfg_data)
                #FIXME what if (sklim_config_path =) not in cfg_data?
        with open(path,'w') as hist_cfg:
            hist_cfg.write(cfg_data)

    logger.info(f'Parsing the histogramming configuration from {path}')
    module = importfile(path)
    if validate(module):
        cfg = dump(module)
        return cfg 
    else:
        return None 

def validate(module):
    try:
        outdir = module.out_dir
        if not isinstance(outdir, str):
            logger.error(f'"out_dir" must be a string')
    except AttributeError:
        logger.error('The histogramming configuration file must have a "out_dir" string')
    try:
        skl_cfg = module.sklim_config_path
        if not os.path.isfile(skl_cfg):
            logger.error(f'Sklimming configuration file {skl_cfg} does not exist.')
    except AttributeError:
        logger.error('The histogramming configuration file must have a "sklim_config_path"\
            string, for the sklimming configuration file')

    parse_client_params(module)
    parse_computation_params(module)
    parse_file_list(module)
    validate_samples(module)
    validate_regions(module)
    validate_systematics(module)
    return True

def validate_samples(module):
    try:
        samples = module.Samples_XP
        if not isinstance(samples, list):
            logger.error(f'The Samples to process must be provided as a list')
    except AttributeError:
        logger.error('The histogramming configuration file must have a "Samples_XP" list')
    sample_names = []
    for sample in samples:
        if not isinstance(sample.name, str):
            logger.error(f"Sample name must be a string, you gave {type(sample.name)} ")
        #TODO: Add checks for other class attributes 
        sample_names.append(sample.name)
    if len(set(sample_names)) != len(sample_names):
        logger.error("All sample names must be unqiue")

    return True

def validate_regions(module):
    try:
        regions = module.Regions
        if not isinstance(regions, list):
            logger.error(f'The regions defined must be provided as a list')
    except AttributeError:
        logger.error('The histogramming configuration file must have a "Regions" list')
    region_names = []
    for region in regions:
        if not isinstance(region.name, str):
            logger.error(f"Region name must be a string, you gave {type(region.name)} ")
        if not isinstance(region.filter, str):
            logger.error(f"Region filter must be a string, you gave {type(region.filter)} ")
        region_names.append(region.name)
    if len(set(region_names)) != len(region_names):
        logger.error("All region names must be unqiue")

    return True

def validate_systematics(module):
    try:
        systs = module.Systematics
        if not isinstance(systs, list):
            logger.error(f'The systematic variations must be provided as a list')
    except AttributeError:
        logger.error('The histogramming configuration file must have a "Systematics" list')
    sys_names = []
    for sys in systs:
        if not isinstance(sys, XP_Systematics):
            logger.error(f"Systematic must inherit from XP_Systematics class, you gave a {type(sys)} object")
        if not isinstance(sys.name, str):
            logger.error(f"Systematic name must be a string, you gave {type(sys.name)} ")
        #TODO: Add checks for subclasses
        sys_names.append(sys.name)
    if len(set(sys_names)) != len(sys_names):
        logger.error("All systematic names must be unqiue")

    return True

def dump(module):
    '''
    Write the information from python module to a dict of configs
    '''
    cfg = {}
    cfg['samples'] = module.Samples_XP
    cfg['regions'] = module.Regions
    cfg['systematics'] = module.Systematics
    cfg['observables'] = module.computation_params['histogram_variables']
    cfg['client_params'] = parse_client_params(module)
    cfg['file_list'] = parse_file_list(module)
    cfg['computation_params'] = parse_computation_params(module)
    cfg['out_dir'] = module.out_dir
    cfg['sklim_config'] = module.sklim_config_path

    return cfg

def parse_client_params(module):
    required_settings = ['n_workers','memory_limit','threads_per_worker']
    try:
        params = module.client_params
        params = {k.lower(): v for k, v in params.items()}
    except AttributeError:
        logger.error(f'The histogramming configuration file must have a "client_params"\
            dictionary with at least the following settings [{required_settings}]')
    if not all (req in params for req in required_settings):
        logger.error(f'The histogramming configuration file must have a "client_params"\
            dictionary with at least the following settings [{required_settings}]') 

    #default_params = {}
#    for k, v in default_params.items():
#        if k not in params:
#            params[k] = v

    return params

def parse_computation_params(module):
    required_settings = ['chunk_size','histogram_variables']
    try:
        params = module.computation_params
        params = {k.lower(): v for k, v in params.items()}
    except AttributeError:
        logger.error(f'The histogramming configuration file must have a "computation_params"\
            dictionary with at least the following settings [{required_settings}]')
    if not all (req in params for req in required_settings):
        logger.error(f'The histogramming configuration file must have a "computation_params"\
            dictionary with at least the following settings [{required_settings}]') 
    return params

def parse_file_list(module):
    required_settings = ['top_directory','file_regex']
    try:
        file_list = module.file_list
        file_list = {k.lower(): v for k, v in file_list.items()}
    except AttributeError:
        logger.error(f'The histogramming configuration file must have a "file_list"\
             dictionary')
    if not all (req in file_list for req in required_settings):
        logger.error(f'The histogramming configuration file must have a "file_list"\
             dictionary')
    return file_list

def update(cfg, args):
    if args.outdir is not None:
        cfg['out_dir'] = args.outdir
    if args.skcfg is not None:
        cfg['sklim_config'] = args.skcfg
    return cfg 

def functional_XP(sample,region,systematic):

    if region == 'default':
        skip = True
    else:
        skip = False
    return (None,None,None,skip) #return region_filter, sample_filter, systematic_weight, skip bool

def get_sklim_samples(sklim_cfg_path, top_dir, regex_str = None):
    sklim_module = importfile(sklim_cfg_path)
    sklim_validate_samples(sklim_module)
    sklim_samples = sklim_module.samples
    sample_list = []
    for item in sklim_samples:
        #if regex_str is None: #FIXME what should be default?
        #    regex_str = item.name + '_chunk0.h5'
        sample_list.append(XP_Sample(name = item.name, regex=True, top_directory = top_dir, file_regex = item.name + '_chunk0.h5'))
    print('sample list',sample_list)
    return sample_list

from typing import Any, Dict, List, Optional, Union
from pathlib import Path 
from utils.common import logger 
from pydoc import importfile
import types
logger = logger.ColoredLogger()

def process(cfg_path: Union[str, Path]) -> Union[Dict[str, Any], None]:
    '''
    Function to read in a python module and dump the information from
    there into a dictionary 
    Args:
        cfg_path: The path to the configuration file
    Returns:
        config: The dictionary holding information from config file
    '''
    path = str(cfg_path)
    logger.info(f'Parsing the Sklimming Configuraiton from {path}')
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
    validate_samples(module)
    #samples = module.Samples_XP
    #TODO: validate regions and systematics, client params, file_list and computation_params
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

def dump(module):
    '''
    Write the information from python module to a dict of configs
    '''
    cfg = {}
    cfg['samples'] = {sample.name: sample for sample in  module.Samples_XP}
    cfg['client_params'] = parse_client_params(module)
    cfg['file_list'] = parse_file_list(module)
    cfg['computation_params'] = parse_computation_params(module)
    cfg['out_dir'] = module.out_dir

    return cfg

def parse_client_params(module):
    required_settings = ['n_workers','memory_limit','threads_per_worker']
    params = module.client_params
    #TODO: validate params
    return params

def parse_computation_params(module):
    required_settings = ['chunk_size','histogram_variables']
    params = module.computation_params
    #TODO: validate params
    return params

def parse_file_list(module):
    file_list = module.file_list
    #TODO: validate file_list
    return file_list

#TODO: use as example for validation    
#def parse_settings(module):
#    required_settings = ['jobname']
#    try:
#        settings = module.general_settings
#        settings =  {k.lower(): v for k, v in settings.items()}
#    except AttributeError:
#        logger.error(f'The Histogramming configuration file must have a "general_settings" dict with at least \
#                      the following settings [{required_settings}]')    
#    
#    if not all (req in settings for req in required_settings):
#        logger.error(f'The Histogramming configuration file must have a "general_settings" dict with at least \
#                      the following settings [{required_settings}]') 
#
#    default_settings = {
#        'skipmissingfiles': False,
#        'dumptoformat': 'H5',
#        'outdir': f"./settings['jobname']/"
#    }
#    for k, v in default_settings.items():
#        if k not in settings:
#            settings[k] = v
#    
#    return settings

def update(cfg, args):
    if args.outdir is not None:
        cfg['settings']['outdir'] = args.outdir
    if args.skip_missing_files is not None:
        cfg['settings']['skipmissingfiles'] = args.skip_missing_files
    return cfg 
from typing import Any, Dict, List, Optional, Union
from pathlib import Path 
from thbbanalysis.common import logger 
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
    validate_samples(module)
    samples = module.samples
    for sample in samples:
        name = sample.name
        for tree, branches in sample.branches.items():
            validate_branches(branches, name, tree)
        validate_selection(sample.selec,  name, sample.branches)
    return True

def validate_selection(selection, sample_name, branches):
    if selection is not None:
        cuts = selection.func
        cut_args = selection.args
        label = selection.label
        if not isinstance(cuts, types.FunctionType):
            logger.error("(Sample {sample.name}) - \n Selection('func',..) must be given as a function")
        if not isinstance(cut_args, dict) or not all(isinstance(v, list) and isinstance(k,str) for k, v in cut_args.items()):
            logger.error("(Sample {sample.name}) - \n Selection(..,'args',..) must be given as a a list of tree (str) to branch names (list)")
        if isinstance(cut_args, dict) and not all(isinstance(elem, (str, float, int)) for k, v in cut_args.items() for elem in v):
            logger.error(f"(Sample {sample.name}) - \n Selection(..,'args',..) is given as a map to a list of objects other than strings, floats or ints ")            
        for tree, args in cut_args.items():
            if tree not in branches:
                logger.error(f"(Sample {sample.name}) - \n Selection(..,'args',..) tree {tree} is not found in the sample branches -- cannot use it for cuts")
        if label is not None:
            if not isinstance(label, (list, str)):
                logger.error(f"(Sample {sample.name}) - \n Selection(..,..,'label') must be a list of strings or a string")
            if isinstance(label, list) and not all(isinstance(elem, str) for elem in label):
                logger.error(f"(Sample {sample.name}) - \n Selection(..,..,'label') must be a list of strings or a string")
            
def validate_samples(module):
    try:
        samples = module.samples
        if not isinstance(samples, list):
            logger.error(f'The Samples to process must be provided as a list')
    except AttributeError:
        logger.error('The Sklimming configuarion file must have a "samples" list')
    sample_names = []
    for sample in samples:
        if not isinstance(sample.name, str):
            logger.error(f"Sample name must be a string, you gave {type(sample.name)} ")
        if not isinstance(sample.branches, dict):
            logger.error(f"(Sample {sample.name}) - \n 'branches' must be provided as map from tree to branches")
        if not isinstance(sample.tag, (list, str)):
            logger.error(f"(Sample {sample.name}) - \n 'tag' must be a string or a list of strings, you gave {type(sample.tag)} ")
        if isinstance(sample.tag, list) and not all(isinstance(elem, str) for elem in sample.tag):
            logger.error(f"(Sample {sample.name}) - \n tag is given as a list of non-string ")
        if not isinstance(sample.location, (list, str)):
            logger.error(f"(Sample {sample.name}) - \n 'where' must be a string or a list of strings, you gave {type(sample.location)} ")
        if isinstance(sample.location, list) and not all(isinstance(elem, str) for elem in sample.tag):
            logger.error(f"(Sample {sample.name}) - \n 'where' is given as a list of non-string ")
        if not isinstance(sample.branches, dict):
            logger.error(f"(Sample {sample.name}) - \n 'branches' must be provided as map from tree to branches")
        sample_names.append(sample.name)
    if len(set(sample_names)) != len(sample_names):
        logger.error("All sample names must be unqiue")
    
    return True

def validate_branches(branches, sample_name, tree):
    for branch in branches:
        if not isinstance(branch.write_name, str): # Check on branch name 
            logger.error(f"(Sample {sample_name}, Tree: {tree}) - \n Branch name must be a string, you gave {type(branch.write_name)}")
        if not isinstance(branch.alg, (types.FunctionType, str)): # Check on branch algorithm 
            logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                            Branch 'alg' must either be a function or a string with branch name in input file")
        if isinstance(branch.alg, types.FunctionType) and  branch.alg_args is None: # check branch algo gets arg if needed
            logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                            You provided a function to calculate new branch but not 'args'")
        if isinstance(branch.alg, types.FunctionType) and  branch.alg_arg_types is None: # check branch algo gets arg types if needed
            logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                            You provided a function to calculate new branch but not 'args_types'")
        if branch.alg_args is not None and branch.alg_arg_types is not None:
            if len(branch.alg_args) != len(branch.alg_arg_types):
                logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                                Branch 'args' and 'arg_types' must have same length")            
        if branch.drop is not None and not isinstance(branch.drop, bool): # check if branches to be dropped correctly
            logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                            You used the 'drop' flag but passed it a non-bool value")
        if branch.args_from is not None: # check if branches from different trees requested correctly 
            if not isinstance(branch.args_from, list): # check args_from is a list
                logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                                You used the 'args_from' attribute but passed it a non-list")
            else:
                if any(not isinstance(tree, str) for tree in branch.args_from): # check contents of list
                    logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n\
                                    You used the 'args_from' attribute but passed it a list of non-strings")      
        
            if len([br_type for br_type in branch.alg_arg_types if br_type not in [str,float,int]]) != len(branch.args_from):
                logger.error(f"(Sample: {sample_name}, Tree: {tree}, Branch: {branch.write_name}) - \n \
                                Branch 'args' and 'arg_types' and 'args_from' must have same length")                            

        # check on branch status 
        acc_status = ['on', 'off', 'new']
        if branch.branch_type.lower() not in acc_status:
            logger.error(f'Branch status can only be one of {acc_status}')
        
    # Check on-off branches not specified at same time 
    requested_branch_status = set([branch.branch_type for branch in branches])
    if 'on' in requested_branch_status and 'off' in requested_branch_status:
        logger.error(f'(Sample {sample_name}, Tree: {tree}) - \n You cannot have branches with status on and off at the same time')
    # Check unique branch names
    branch_names = [branch.write_name for branch in branches]
    if len(set(branch_names)) != len(branch_names):
        logger.error("All branch names must be unqiue")
    return True


def dump(module):
    '''
    Write the information from python module to a dict of configs
    '''
    cfg = {}
    cfg['samples'] = {sample.name: sample for sample in  module.samples}
    cfg['settings'] = parse_settings(module)
    return cfg

def parse_settings(module):
    required_settings = ['jobname']
    try:
        settings = module.general_settings
        settings =  {k.lower(): v for k, v in settings.items()}
    except AttributeError:
        logger.error(f'The Sklimming configuarion file must have a "general_settings" dict with at least \
                      the following settings [{required_settings}]')    
    
    if not all (req in settings for req in required_settings):
        logger.error(f'The Sklimming configuarion file must have a "general_settings" dict with at least \
                      the following settings [{required_settings}]') 

    default_settings = {
        'skipmissingfiles': False,
        'skipmissingsamples': False,
        'dumptoformat': 'H5',
        'outdir': f"./{settings['jobname']}/",
        'yields': True, 
    }

    for k, v in default_settings.items():
        if k not in settings:
            settings[k] = v
    
    return settings

def update(cfg, args):
    if args.outdir is not None:
        cfg['settings']['outdir'] = args.outdir
    if args.skip_missing_files is not None:
        cfg['settings']['skipmissingfiles'] = args.skip_missing_files
    return cfg 
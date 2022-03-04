''' 
author: Mohamed Aly (maly@cern.ch)
Brief: Functions to set up file paths and read sample data into awkward arrays using uproot methods
'''
#=========== File Reading Imports
import uproot4 as uproot
from pathlib import Path
import awkward as ak 
import numpy as np
#============== System and Python Imports
from typing import List, Dict, Tuple
import glob, os
import regex as re
import time
import psutil
import gc
#============ thbbanalysis Imports
from utils.common.branches import *
from utils.common.tools import combine_list_of_dicts
import utils.sklimming as sklim
from utils.common import tools



CfgType = Dict[str, Dict[str, Union[str,bool,int,float]]]
SampleDataType = Dict[str, List[Union[str,float,int]]]
CutFuncType = Callable[..., "ak.Array"]
CutFuncArgsType = Dict[str,List[Union[str,float,int]]]
BranchStatusType = Dict[str,Dict[str,List[Union["Branch",str]]]]


def decorate_sample_tag(tags:List[str])->List[str]:
    '''
    Take a list of unique sample tags and decorate it with wildcards
    Args:
        tags:  A list of sample identifying tags
    Return:
        a list with decorated elements
    '''
    return [f'*{tag}*' for tag in tags]


def make_sample_path(locations: List[Path], tags:List[str]) -> List[str]:
    '''
    Attach path pieces together to make a list of valid paths to look for sample files
    Args:
        locations: The directories to look for sample
        tags: The decorated tags to identift sample
    Return:
        paths: A list of full paths up to sample tags
    '''
    paths = [str(loc)+'/'+tag for tag in tags for loc in locations]
    dirpaths = [p+'/*'  for path in paths for p in glob.glob(path) if os.path.isdir(p)]
    fpaths = list(set([path  for path in paths for p in glob.glob(path) if not os.path.isdir(p) ]))
    paths = dirpaths+fpaths
    return paths


def process_sample(sample: "Sample", cfg: CfgType)->Dict[str, "ak.Array"]:
    '''
    This is the High level function which sets up the pieces needed to call uproot and pass the information to reader
    for each tree to be extracted from sample files
    Args:
        sample: The sample object carrying information
        cfg: A dictionary carrying all settings specified in config file
    Return:
        None
    '''
    logger.info(f'Processing the following sample: {sample.name}')
    locs = sample.location
    tags = decorate_sample_tag(sample.tag)
    trees_to_branch_names = {}
    trees_to_status_to_branches = {tree:{} for tree in sample.branches}
    tree_to_branch_write_names = {tree: [branch.write_name for branch in branch_list] for tree, branch_list in sample.branches.items()}
    paths = make_sample_path(locs, tags)
    for tree, branch_list in sample.branches.items():
        branch_write_names = tree_to_branch_write_names[tree]
        on_branch_names = [branch.alg for branch in branch_list if branch.branch_type == 'on']
        on_branches = [branch for branch in branch_list if branch.branch_type == 'on']
        new_branches = [branch for branch in branch_list if branch.branch_type == 'new']
        tmp_branches = [branch for branch in branch_list if branch.drop is True]
        # required branch names to compute new branches -- not Branch objects. 
        req_branches = [arg for branch in new_branches 
                        for idx, arg in enumerate(branch.alg_args) 
                        if (branch.alg_arg_types[idx]== Branch 
                        and (branch.args_from is None or branch.args_from[idx] == tree)
                        and arg not in branch_write_names)]
        
        branch_names = list(set(on_branch_names+req_branches))
        trees_to_branch_names[tree] = branch_names
        trees_to_status_to_branches[tree]['on'] = on_branches
        trees_to_status_to_branches[tree]['req'] = req_branches
        trees_to_status_to_branches[tree]['new'] = new_branches
        trees_to_status_to_branches[tree]['tmp'] = tmp_branches
    
    if sample.selec is not None:  # add branches needed just for cuts to req_branches
        for tree, args in sample.selec.args.items():
            branch_write_names = tree_to_branch_write_names[tree]
            req_branches = [arg for arg in args if isinstance(arg, str) and arg not in branch_write_names]
            trees_to_status_to_branches[tree]['req'] += req_branches
    
    run_workflow(paths, trees_to_branch_names, sample, cfg, trees_to_status_to_branches)


def run_workflow(paths: List[str], trees_to_branch_names: Dict[str, str], sample: "Sample", cfg: CfgType, trees_to_status_to_branches: BranchStatusType)->Dict[str,"ak.Array"]:
        '''
        Method responsible for running the pre-processing workflow, starting from file reading, 
        followed by manipulating input then writing out data. The workflow cycle is done on chunks of files
        Args:
            paths: the list of paths to look for sample
            trees_to_branch_names: A map from tree names to branches to be extracted from tree
            sample: The Sample object being procssed 
            cfg: A dictionary carrying all settings specified in config file
            trees_to_status_to_branches: Map for each sample from tree to various status 
                                of branches to branches that match that status.
                                Status can be on, off, new, req, tmp.
        Return:
            None 
        '''
        skip_missing_files = cfg['settings']['skipmissingfiles']
        if len(paths)==0:
            logger.error("Input paths not found..")
        for path in paths:
            logger.info(f'Processing data from the following path: \n {path}')
            files = glob.glob(path) # Get list of files matching path regex
            if len(files) == 0:
                logger.warning(f"No files were found in {path}, skipping")
                continue 
            try:
                # split files into list(list) where inner list of files total size < 4GB
                data_chunks = chunk_files(files) 
                # int to keep track of how many chunks were processed smoothly
                done=0
                # Loop over groups of 4GBs file sets
                for chunk_index, chunk in enumerate(data_chunks):
                    logger.info(f"Reading data from with uproot for chunk {chunk_index+1}/{len(data_chunks)}")
                    exception = 0
                    # While there are still exceptions in reading the file, remove file causing exception and re-read
                    while exception is not None:
                        chunk_data, exception = read(chunk, trees_to_branch_names)
                        # If all files were read succesfully break before code tries to find errors
                        if exception is None:   break
                        broken_file = handle_exception(exception, skip_missing_files) 
                        # if exception handled remove file with missing key
                        chunk.remove(broken_file)
                        # re-read rest of files. If exception is still not None, while loop starts over to remove next file
                        chunk_data, exception = read(chunk,trees_to_branch_names)
                    logger.info(f"Manipulating chunk data")
                    chunk_data = finalize(chunk_data,  sample, trees_to_status_to_branches)
                    if len(chunk_data)!=0:
                        logger.info(f"Writing chunk data")
                        sklim.writer.write_sample(chunk_data, sample, cfg , suffix='_chunk'+str(chunk_index))
                        done += 1
                        # Clean up memory
                        del chunk_data
                        gc.collect()
                    else:
                        logger.warning(f"No data from chunk, not written out")
                if done == 0:
                    logger.error(f"No data saved from any chunks. Are you cutting too harshly?")
            # If some other error was found which is not caught by the process() function, display it and break
            except Exception as not_uproot_except:
                raise not_uproot_except

def chunk_files(files: List[str]) -> List[List[str]]:
    '''
    Method to split a list of file to a list of lists with inner lists
    total size of files < 4GB. 

    Args:
        files: The list of file paths to chunk up
    Return
        list of lists of file paths
    '''
    chunks: List[List[str]] = []
    chunk_of_files: List = []
    chunk_size: float = 0
    for file in files:
        # Add current file to chunk size. If files[i] != files[0]
        # and files[i-1] is < 2GB,  chunk size would already have
        # value chunk_size = size(files[i-1]). Else, chunk_size = 0
        chunk_size+=os.path.getsize(file)*1e-9  # in GB
        # If chunk size still less than 2GB
        if chunk_size <= 2. : # in GB
            # Append file to chunk
            chunk_of_files.append(file)
            # If we have added all files to a chunk but total size still < 4GB
            if file == files[-1]:
                # just append the chunk of files and we're done
                chunks.append(chunk_of_files)
        # If chunk_size+=size(files[i]) goes above 2 GB
        else:
            # if size(files[i-1]) was < 2 GB, chunk_of_files = [files[k],..,files[i-1]]
            # otherwise chunk_of_files = []
            if chunk_of_files != []:  
                # store the list of files with total size < 2 GB
                chunks.append(chunk_of_files)
                # Clear up the chunk for new set of files
                chunk_of_files = []
            # Append files[i] to a new chunk
            chunk_of_files.append(file)
            # Reset the chunk size 
            chunk_size = 0
            # If size(files[i]) > 2 GB, it gets its own chunk
            if os.path.getsize(file)*1e-9 > 2.:
                chunks.append(chunk_of_files) # store chunk [files[i]] 
                chunk_of_files = [] # clear array for next files[k>i]
            else:
                # If files[i] < 2GB, add its size to new chunk size
                chunk_size+=os.path.getsize(file)*1e-9

    return chunks


def read(chunk_files: List[str], trees_to_branch_names: Dict[str, str])-> Tuple[Optional[Dict[str, "ak.Array"]], Optional[Exception]]:
    '''
    Function that calls uproot concatenate/iterate based on file sizes, catching exceptions while reading
    Args:
        file_list: A list of files whose size add up to <= 4GBs
        trees_to_branch_names: A map from tree names to branches to be extracted from tree
    Return 
        If no exception arises:
            ({tree: ak.Array}, None) 
        else:
            (None, exception)

    '''

    # If the chunks are empty, we have removed all files in exception handling
    if len(chunk_files) == 0:
        logger.error("Chunk of files is empty. If files have been skipped, this might mean all files could not be read")
    
    chunk_data = {}
    for tree, branches in trees_to_branch_names.items():
        start_t = time.time()
        logger.info(f"Reading data from the following tree: {tree} ")
        # Add tree to chunk names
        chunk_tree = list(map(lambda ls: ls+f':{tree}', chunk_files))
        try:
            # If only one file in chunk, it can be a huge file > 4GB
            # or file that didn't fit in previous chunk. Eitherways, use uproot.iterate
            if len(chunk_files) == 1:
                data = []
                logger.info(f"Using uproot.iterate .... ")
                for batch in uproot.iterate(chunk_tree, branches):
                    data.append(batch)
                chunk_data[tree] = ak.concatenate(data)
            else:
                logger.info(f"Using uproot.concatenate .... ")
                data = uproot.concatenate(chunk_tree, branches, library='ak')
                logger.info(f"Storing data memory_info().rss (GB) = {psutil.Process(os.getpid()).memory_info().rss / 1024 ** 3}")
                chunk_data[tree] = data
        except uproot.exceptions.KeyInFileError as uproot_except:
            return None, uproot_except
        except Exception as other_except:
            return None, other_except
        finish_t = time.time()
        logger.info(f"Time taken processing {tree} from chunk: {finish_t-start_t}")
    return chunk_data, None


def handle_exception(exception: Exception, skip_missing_files: bool)->Optional[str]:
    '''
     Method to decide what do with an exception while reading data and raise
     appropriate logging to alert user
     Args:
        exeption: The exception caught while reading data
        skip_missing_files: bool to decide whether code should break on faulty files
    Return:
        broken_file: Name of file broken, only if user asks to skip faulty files.
    '''
    broken_file = re.findall(r"in file .*\..*",str(exception))
    broken_file = broken_file[0].replace("in file ", "") if len(broken_file)>=1 else None
    missing_key = re.findall(r"not found: '.*'",str(exception))
    missing_key = missing_key[0].replace("not found: ", "").strip("'") if len(missing_key)>=1 else None
    if missing_key is not None and broken_file is not None:
        if not skip_missing_files:
            logger.error(f"Missing key {missing_key} in file {broken_file} ")
        else:
            logger.warning(f"Missing key {missing_key},  skipping broken file {broken_file}")
    elif missing_key is None and broken_file is not None:
            if not skip_missing_files:
                logger.error(f"Broken file {broken_file} with Error: \n {str(exception)}")
            else:
                logger.warning(f"Skipping broken file {broken_file}")
                logger.warning(f"Error: \n {str(exception)}")
    # If some other excpetion where there is no specific file, break code
    else:
        raise exception
        logger.error(exception)    
    return broken_file


def finalize(chunk_data: "Dict[str,ak.Array]", sample: "Sample", trees_to_status_to_branches: BranchStatusType):
    '''
    Method to add new branches to data, apply cuts, then drop unwanted branches
    Args:
        chunk_data: A dict from tree to awkward array of data from one chunk
        sample: The Sample object being processed
        trees_to_status_to_branches: Map for each sample from tree to various status 
                                     of branches to branches that match that status.
                                     Status can be on, off, new, req, tmp.
    Return:
        chunk_data: Same as arg, but after manipulation
    '''

    finished_data = []
    chunk_data = add_branches(chunk_data, trees_to_status_to_branches)
    if sample.selec is not None:
        chunk_data = apply_cuts(chunk_data, sample.selec)
    chunk_data = drop_branches(chunk_data, trees_to_status_to_branches)
    return chunk_data


def add_branches(trees_to_data: SampleDataType, trees_to_status_to_branches: BranchStatusType):
    '''
    Function to create new branches that user has requested or to simply rename branches that
    were read from input to the name assigned to them by user. This step must be ran before the
    `apply_cuts` method since the user can request cuts to be applied on new branches or on the
    given name to branches read from inputs. 
    Args:
        trees_to_data: Map for each sample from tree to all the data read from that tree
        trees_to_status_to_branches: Map for each sample from tree to various status 
                                     of branches to branches that match that status.
                                     Status can be on, off, new, req, tmp.
    Return
         Map for each sample from tree to all the data read from that tree after filters are applied 
    ''' 

    for tree, data in trees_to_data.items():    
        new_branches = trees_to_status_to_branches[tree]['new']
        on_branches = trees_to_status_to_branches[tree]['on']    
        for branch in on_branches:
            data[branch.write_name] = data[branch.alg] # this creates new branch, unless keys match
            if branch.write_name != branch.alg: # don't drop the branch if it's name hasn't changed 
                data = data[[x for x in ak.fields(data) if x != branch.alg]]
        data = create_new_branches(data, new_branches)
        trees_to_data[tree] = data 
    
    # Loop again to compute new branches that need args from different trees. 
    for tree, data in trees_to_data.items():
        new_branches = trees_to_status_to_branches[tree]['new']
        on_branches = trees_to_status_to_branches[tree]['on']
        data = create_new_branches(data, new_branches, mix_trees=True, trees_to_data=trees_to_data)
        trees_to_data[tree] = data
    
    trees_to_data = {tree:data for tree,data in trees_to_data.items() if data is not None}
    return trees_to_data


def create_new_branches(data: "ak.Array", new_branches: List["Branch"], mix_trees: bool = False, trees_to_data: Optional[SampleDataType] = None):
    '''
    Function to compute new branches, taking care of the case when new branches need
    other new branches to be computed first to be then passed as args to the algo. 
    Args:
        data: Awkward array of data for one tree -- can be thought of as a dict
        new_branches: A list of Branch objects that need to be computed 
        mix_trees: Flag to determine if branches to be computed from multiple trees are allowed
        trees_to_data: Map for each sample from tree to all the data read from that tree 
                       (only needed to compute branches from multiple trees)
        
    Return
          Awkward array of data for one tree with new branches added
    ''' 
    new_branches_from_others: List["Branch"] = [] 
    for branch in new_branches:
        # if we need other new branches to compute this new branch, save it for later
        if len(set([br.write_name for br in new_branches]).intersection(set(branch.alg_args)))!=0:
            new_branches_from_others.append(branch)
            continue

        # if branches computed from multiple trees is not allowed 
        if not mix_trees:  # (initial call to this method comes here)
            if branch.args_from is None: #  check the branch doesn't need args from multiple trees
                # Get args and execute the new beanch algo 
                args = [data[arg] if branch.alg_arg_types[i] == Branch else arg for i, arg in enumerate(branch.alg_args)]
                if branch.isprop:
                    if len(args)>1:
                        logger.error(f"Branch {branch.write_name} is supposed to be a propery of another branch, but you passed multiple args to 'args'")
                    else:
                        arg = args[0]
                        data[branch.write_name] = getattr(arg, branch.alg)
                else:
                    data[branch.write_name] = branch.alg(*args)

        else: 
            if branch.args_from is not None: # only care to process branches from mixed trees
                args_from = branch.args_from  # get tree names 
                # get branches from trees and execute new branch algo 
                args = [trees_to_data[args_from[i]][arg] if branch.alg_arg_types[i] == Branch else arg for i, arg in enumerate(branch.alg_args)]
                data[branch.write_name] = branch.alg(*args)
    # If we have anu branches that are saved for later proessing, 
    # re-run the method on them with the updated data containing new branches
    if(len(new_branches_from_others)!=0):
        data = create_new_branches(data, new_branches_from_others, mix_trees=mix_trees, trees_to_data=trees_to_data)
    return data


def apply_cuts(trees_to_data: SampleDataType, sel: CutFuncType)-> SampleDataType:
    '''
    Function to filter data based on sample selection cuts provided in the configuration file. The branches
    specified to be cut on must have names specified as `sample.write_name` -- not the name in the input, unless
    both match. 
    Args:
        trees_to_data: Map for each sample from tree to all the data read from that tree
        cuts: A function to be called with awkward arrays as args in order to filter the data
        cut_args: A map for each sample from tree to the branches (or tree-independent objects like floats) 
                  needed to filter the data to be passed as arguments to the `cuts` function
    Return
         Map for each sample from tree to all the data read from that tree after filters are applied 

    ''' 
    cut_args = sel.args
    cuts = sel.func
    for tree, args in cut_args.items():
        data = trees_to_data[tree]
        args = [data[arg] if isinstance(arg,str) else arg for arg in args]
        data = data[cuts(*args)]
        if len(data) != 0: # if we haven't filtered out all data
            trees_to_data[tree] = data
        else:
            trees_to_data[tree] = None
    return trees_to_data


def drop_branches(trees_to_data: SampleDataType, trees_to_status_to_branches: BranchStatusType):
    '''
    Function to drop branches that user did not ask to save. These can be 
    1. Branches saved to be used in creating new branches
    2. Branches with the drop attribute activated by user in config
    3. Branches needed to apply selection cuts on them 
    Args:
        trees_to_data: Map for each sample from tree to all the data read from that tree
        trees_to_status_to_branches: Map for each sample from tree to various status 
                                     of branches to branches that match that status.
                                     Status can be on, off, new, req, tmp.
    Return
         Map for each sample from tree to all the data read from that tree after filters are applied 
    ''' 
    for tree, data in trees_to_data.items():
        new_branches = trees_to_status_to_branches[tree]['new']
        req_branches = trees_to_status_to_branches[tree]['req']
        tmp_branches = trees_to_status_to_branches[tree]['tmp']          
        for branch in req_branches: # these are just branch names
            data = data[[x for x in ak.fields(data) if x != branch]]
        for branch in tmp_branches:
            data = data[[x for x in ak.fields(data) if (isinstance(branch.alg,str) and x != branch.alg) or (not isinstance(branch.alg,str) and x!=branch.write_name)]]
        if len(data) != 0:
            trees_to_data[tree] = data
        else:
            trees_to_data[tree] = None
    trees_to_data = {tree:data for tree,data in trees_to_data.items() if data is not None}
    return trees_to_data




        

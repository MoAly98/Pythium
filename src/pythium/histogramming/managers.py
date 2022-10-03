'''
This is where manage different parts of the histogramming stage :py:class:`pythium.histogramming.managers._InputManager`
'''

# Python Imports
import os
from glob import glob 
from collections import defaultdict
import re
import numpy as np
# Scikit-HEP 
import dask
from hist import Hist
import hist
import awkward as ak
# Pythium
from pythium.common.tools import h5py_to_ak, json_to_ak, parquet_to_ak
from pythium.histogramming.objects  import Observable, NTupSyst, TreeSyst, WeightSyst, CrossProduct
from pythium.histogramming.binning import _Binning
from pythium.common.functor import Functor
from pythium.common.logger import ColoredLogger

logger = ColoredLogger()

class _InputManager(object):

    '''
    Class responisble for preparing information about the 
    input files and what we want from them
    '''
    def __init__(self, xps, cfg):
        '''
        _InputManager constructor 

        Args:
            xps (List[CrossProduct]): A list of the cross-products to be evaluated
            cfg (dict): The histogramming configuration dictionary
        '''
        
        # Define the map from input format to read method
        read_methods = {
                        'parquet': 'ak_parquet',
                        'json': 'ak_json',
                        'root': 'uproot',
                        'h5': 'ak_h5'
                        }
        self.xps = xps
        self.indirs = cfg["general"]["indir"]
        self.from_pyth = cfg["general"]["frompythium"]
        self.ext = cfg["general"]["informat"]
        self.sample_sel = cfg["general"]["samplesel"]
        self.reader = read_methods[self.ext]
    
    def required_variables(self):
        '''
        Method to determine which variable columns need to be retrieved from input files.
        Required variables are gathered from:

        - Variables directly requested with the `Observable('variable','name')` API
        - Variables required to compute new `Observable` s (either passed as args or inferred from a string)
        - Weights column
        - Variables required to apply a region seleciton
        - Variables required to compute a weight variation
        
        These variables are encoded in `Functor` instances for each 
        `Observable`, `Selection` and `WeightSyst` instances, as the attribute req_vars  

        Returns:
            Mapping from `CrossProduct` instances to list of required variables passed as `Observable` instances
        '''
        
        # To return Observable() instances, need some binning (which will not be used)
        dummy_binning =  [_Binning([1.,2.,3.])]
        # Declare the map to be returned 
        xp_to_req = defaultdict(list)
        new_vars_names= [ xp["observable"].name for xp in self.xps  if xp["observable"].builder.new ]
        for xp in self.xps:

            sample, region, obs, systematic, template = xp
            
            # Declare lists for different orirgins of required variables
            required_variables = []
            obs_vars, _region_sel_vars, sample_sel_vars, syst_vars = [],[],[],[]
            
            # Get required variables for the current observable
            # excluding variables that need to be built 
            obs_vars = [ Observable(reqvar, reqvar, dummy_binning, obs.dataset) 
                         for reqvar in obs.builder.req_vars 
                         if reqvar not in new_vars_names
                        ]
            
            # If weight is given as a column name and is not a column that still need to be built
            # then also grab it from input
            if isinstance(obs.weights,str):
                if obs.weights not in new_vars_names:
                    obs_vars.extend([Observable(obs.weights, obs.weights, dummy_binning, obs.dataset) ] )
            
            # If a region is defined, then a selector is defined and we should get variables required to apply cuts
            region_sel_vars =  [ Observable(reqvar, reqvar, dummy_binning, obs.dataset) for reqvar in region.sel.req_vars ] 
            # if user flags that a Sample selection is applied at histogramming stage, get required variables to apply cuts
            if self.sample_sel:
                sample_sel_vars =  [ Observable(reqvar, reqvar, dummy_binning, obs.dataset) for reqvar in sample.sel.req_vars ]
            
            # If the cross product involves a  weight systematic, need to grab required variables
            if isinstance(systematic, WeightSyst):
                template = getattr(systematic, template)

                # If the weight is defined by a function then we need the args for this function
                if isinstance(template, Functor):
                    syst_vars =  [ Observable(reqvar, reqvar, dummy_binning, obs.dataset) for reqvar in template.req_vars ] 
                # else, the weight is just in the input or will be built as a new variable
                else:
                    if template not in new_vars_names:                    
                        syst_vars = [ Observable(template, template, dummy_binning, obs.dataset) ]  
            
            # Required variables is the combination of all variables we found are needed
            required_variables.extend(obs_vars+region_sel_vars+sample_sel_vars+syst_vars)
            xp_to_req[xp] = list(set(required_variables)) # Remove duplicates

            
        return xp_to_req

    def required_paths(self):
        '''
        Method to summarise all the input files that need to be opened.
        
        Goal is to have the task manager open each file only once and get what's needed from it. 
        The paths are constructed for each XP assuming Pythium naming system, where
        a file is defiend by a sample + dataset.

        Paths are gather from (In case of Pythium-like input):

        - Paths to the nominal file needed for an observable
        - Path to an alternative sample needed for an NTup systematic
        - Path to an alternative tree needed for a Tree systematic
        
        TODO:: Support Custom inputs 
        '''

        xp_to_paths = defaultdict(list)
        for xp in self.xps:
            
            sample, region, observable, systematic, template = xp
            
            if self.from_pyth:  # Follow pythium naming scheme

                # Get the sample and observable in the current XP
                sample_name = sample.name
                obs_dataset = observable.dataset
                # Build a regex path to be globbed using the file-extenstion provided by user and
                # all the paths the user told us to look in
                paths = [f"{path}/{sample_name}__*__{obs_dataset}*.{self.ext}".replace('//','/') for path in self.indirs]
                
                # If this is not a nominal histogram, then we may have NTuple or Tree variations
                if template != 'nom':
                    # If we have an Ntuple variation, then we want to access same dataset but different sample 
                    if isinstance(systematic, NTupSyst):
                        # User can ask to look in some other directory different from general setting
                        sys_dirs =    getattr(systematic, "where", [None])
                        sys_samples = getattr(systematic, template)
                        if sys_dirs == [None]:
                            paths = [f"{indir}/{s_samp}__*__{obs_dataset}*.{self.ext}".replace('//','/') for indir in indirs for s_samp in sys_samples]
                        else:
                            paths = [f"{s_dir}/{s_samp}__*__{obs_dataset}*.{self.ext}".replace('//','/') for s_dir in sys_dirs for s_samp in sys_samples]
                    
                    # If we have a Tree variation, then we want to access a different dataset but same sample 
                    elif (isinstance(systematic, TreeSyst)):
                        syst_dataset = getattr(systematic, template) 
                        paths = [f"{indir}/{sample_name}__*__{syst_dataset}*.{self.ext}".replace('//','/') for indir in self.indirs]

                # Glob and remove duplicates
                paths = list(set([p for path in paths for p in glob(path) if not os.path.isdir(p) ]))
                xp_to_paths[xp] = paths
               
            else:
                '''
                TODO:: Assume user defined (somehow?) #Custom? some supported special types? decoreator for custom?
                '''
                logger.warning("Only outputs from Pythium currently supported")
                pass

        return xp_to_paths

class _TaskManager(object):
    '''
    Class responsible for building a task-graph from 
    a variety of operations on the input data. In order
    the manager will build the following workflow into a
    graph:

    - Retrieve data from inputs
    - Create new variables needed 
    - Loop through cross-products
    - Apply event cuts (on all columns)
    - Retrieve the relevant observable column
    - Retrieve the relevant weights (can be columns/floats)
    - Make and fill histogram with observable and weights

    '''
    def __init__(self, method, sample_sel):
        '''
        Constructor for `_TaskManager`
        Attributes:
            method (str):       Method name to-be-used for reading input
            sample_sel (bool):  Should sample selections be applied or not
        '''
        # Mapping from method to function that implements this method
        readers = {
                    'ak_parquet': parquet_to_ak,
                    'ak_json': json_to_ak,
                    'ak_h5': h5py_to_ak,
                    'uproot': NotImplementedError("Unsupported input type")
                    }
        self.reader = readers[method]
        self.sample_sel = sample_sel
    

    @dask.delayed
    def _get_data(self, inpath, observables):
        '''
        Call the method to retrieve data from one input file

        Args:
            inpath (str):   Path to file which should be opened 
            observables (List[Observable]): List of `Observable` instances of variables 
                                            to be retrieved from input file for the given
                                            path
    
        Returns:
            An awkward array of data columns retrieved from input path
        '''
        data = self.reader(inpath, [vvar for v in observables for vvar in v.var ])
        return data

    @dask.delayed
    def sort_xps(self, xps):
        '''

        Sort the cross product order so that all new variables that do not depend on other
        new variables are computed first. This makes the creation of the variables less problematic
        and avoids need for recursion which is bad practice in dask.delayed() funcitons.
        
        Args:
            xps (List[CrossProduct]):  List of cross-products whose histograms need 
                                       to be computed for the given input path
        
        Returns:
            Ordered list of cross-products such that XPs that use 
            new variables which in-turn require other new variables 
            are computed last. 
        '''

        now, later = [], []
        # Loop over XPs relevant to the given input path
        for xp in xps:
            
            # Retrieve the observable and its builder 
            observable = xp["observable"]
            builder = observable.builder
            # Make a list of new variables names
            new_vars_names = [ crossprod["observable"].name for crossprod in xps if crossprod["observable"].builder.new]
            # If the builder of the current variable require a new variable, it should be computed at the end
            if len( set([new_varname for new_varname in new_vars_names]).intersection(set(builder.req_vars))) !=0:
                later.append(xp)
            else:   now.append(xp)
        
        return now+later # in that order

    @dask.delayed
    def _create_variables(self, data, xps):
        ''' 
        Compute and add new columns to the data if needed
        
        Args:
            data (ak.Array):   Data columns retrieved from input path
            xps (List[CrossProduct]): The compute-from-file-first ordered list of XPs 
                                      for a given path
        
        Return:
            Awkward array with new columns added 
        '''

        '''
        TODO:: Create variables for systematics?
        '''

        new_data = data
        # Loop through xps for a given path
        for xp in xps:
            
            # Retrieve the observable builder
            observable = xp["observable"]
            builder = observable.builder
            
            '''
             Note for ndim observables, this is currently useless
             since we make the ND histogram by unpacking the
             relevant N variables. 
             TODO:: Find a way to support N-DIM array evaluation 
             into the data table somehow then we can just retrieve it.
            '''
            
            # If observable name is already a column, nothing to do
            if observable.name in data.fields:  continue

            # If observable is just grabbed form input and renamed, nothing to do
            # If user renames an observable, this is only reflected in the histogram
            # name, but not when constructing other variables (funcs must use name in input)
            if len(observable.var) == 1 and not builder.new:    continue 

            # Evaluate the builder of that observable and add it as a column
            # with the user-given name
            new_data[observable.name] = builder.evaluate(data)

            # Special case where a weight is given as an array to Observable
            # Assume it's same length as NEvents and add it as a column 
            if not isinstance(xp["observable"].weights, (str, float, int)):
                if len(xp["observable"].weights) != len(new_data[new_data.fields[0]]):
                    logger.error(f'Weights array provided for {observable.name} has wrong length')
                new_data['__pythweight__'] = xp["observable"].weights
        
        return new_data
    
    @dask.delayed
    def _apply_cut(self, data, xp):
        '''
        Apply event selection onto all columns. Object-wise selection
        should be appplied in the form of masks. 
        
        Args:
            data (ak.Array):   Data columns retrieved from input path
            xps (List[CrossProduct]): The compute-from-file-first ordered list of XPs 
                                      for a given path
        Return:
            Awkward array with event selection applied to columns
        '''
        
        '''
        FIXME:: Override or combine selection?
        '''

        new_data = data
        sample = xp["sample"]
        region = xp["region"]
        # 1st apply overall cuts
        '''
        TODO:: What about overall cuts to apply to all histos?
        '''
        
        # 2. Apply sample cuts
        if sample.sel is not None and self.sample_sel:
            new_data = new_data[sample.sel.evaluate(new_data)]

        # 3. Apply region cuts
        new_data = new_data[region.sel.evaluate(new_data)]
        
        '''
        TODO:: 4. Apply observable cuts
        '''

        return new_data

    @dask.delayed
    def _make_histogram(self, var_data, weights, xp):
        '''
        Method to create and fill a histogram using data from 
        one path that contributes to a given XP histogram. 

        Args:
            var_data (ak.Array):        A column/columns of data which should fill the histogram
            weights (ak.Array | float): The event weight to be used to fill the histogram
            xp (CrossProduct):          The XP instance holding information on the current histogram
        
        Return:
            A filled `Hist` object
        '''
        observable = xp["observable"]
        axes = observable.axes
        h = Hist(*axes, name = observable.name, storage=hist.storage.Weight())
        '''
        TODO:: Data rendering for masking problems
        '''
        var_arrs = []
        for field in var_data.fields:   var_arrs.append(var_data[field])
        h.fill(*var_arrs, weight = weights)
        return h

    
    @dask.delayed
    def _get_var(self, data, xp):
        '''
        Method to retrieve a column from data.
        
        Args:
            data (ak.Array):   Data columns retrieved from input path
            xp (CrossProduct): The XP being computed
        
        Return:
            Awkward array with the relevant column's data
    
        '''
        observable = xp["observable"]
        '''
        .var vs .name:
        * if grab from file:  We grabbed and saved a obs.var column, so can access that
        * if grab fron func:  obs.var == obs.name by construction (since the names from file are in args)
        # if grab from str:   obs.var == obs.name by construction (since the names from file are in string)
        '''
        var = data[observable.var]

        systematic = xp["systematic"]
        '''
        TODO:: Variable in systematic ?
        '''
        return var

    @dask.delayed
    def _get_weights(self, data, xp):
        '''
        Method to compute event weights from different sources.
        For example, if weights are given to an observable, as 
        well as to a WeightSystematic, then we need to multiply both
        
        Args:
            data (ak.Array):   Data columns retrieved from input path
            xp (CrossProduct): The XP being computed
        
        Return:
            Awkward array with the relevant weight column's data or a float
        '''

        # Start with a unit weight
        weights = 1.
        '''
        TODO:: overall weight from general settings
        '''
        # If sample is a data sample, weights are unity
        if xp["sample"].isdata:    return weights

        #================ Observable weights 
        observable = xp["observable"]
        obs_weights = observable.weights
        
        # If weight has been provided as an array
        # to observable constructor, then we saved
        # it as a __pythweight__ column
        if '__pythweight__' in data.fields:
            obs_weights = data['__pythweight__']
        
        # If weight is a string, assume it's a column name
        if isinstance(obs_weights, str):
            obs_weights = data[obs_weights]
        
        # Multiply column/float with current weight
        weights = weights*obs_weights
        
        #================ Systematic weights 
        systematic = xp["systematic"]
        
        # Need extra weight if systematic is a Weight Variation
        if isinstance(systematic, WeightSyst):
            syst_weights = getattr(systematic, xp["template"])
            # If the weight is given as a functor, need to compute it
            if isinstance(syst_weights, Functor):
                syst_weights = syst_weights.evaluate(data)
            # otherwise we just have to grab it
            elif isinstance(weights, str):
                syst_weights = data[syst_weights]
            weights = weights*syst_weights
            
        #================ Region weights
        region = xp["region"]
        region_weights = region.weights
        if isinstance(region_weights, str):
            region_weights = data[region_weights]
       
        weights = weights*region_weights
        return weights 
    
    def paths_to_xpinfo(self, xp_to_paths, xp_to_vars):  
        '''
        Method to convert XP -> paths and XP -> required variables
        maps into path -> xp and path -> required variables maps
        '''  

        path_to_xp = defaultdict(list)
        path_to_vars = defaultdict(list)
        for xp, paths in xp_to_paths.items():
            for path in paths:
                path_to_xp[path].append(xp)
                # No need for XP boundary in required_variables
                # since all required_variables for xps needing this
                # path should be available in the path
                path_to_vars[path].extend(xp_to_vars[xp])
        
        return path_to_xp, path_to_vars
    
    def _build_tree(self, xp_paths_map, xp_vars_map):
        '''
        Method to build an optimized task graph of the entire
        histogramming chain.
        
        Args:
            xp_paths_map: Mapping from XP to paths needed
            xp_vars_map:  Mapping from XP to variables needed
        
        Return:
            List of dask tasks to be executed
            Corresponding list of XPs (matches the list of jobs)

        '''


        # Conver maps such that paths are keys so that
        # we open each path once and get info needed for 
        # all xps, instead of opening it once-per-xp that needs it
        paths_to_xp, path_to_vars = self.paths_to_xpinfo(xp_paths_map, xp_vars_map)
        
        # Mapping to store all filled histograms from all paths
        # contributing to each XP
        xp_to_hists = defaultdict(list)

        for path, _ in paths_to_xp.items():
            xps = paths_to_xp[path]
            variables = path_to_vars[path]
            # Retrieve all relevant data from input path
            data = self._get_data(path, list(set(variables)))
            # Sort the XPs that need this data in order of computation
            sorted_xps = self.sort_xps(xps)
            # Create new variables as needed
            data = self._create_variables(data, sorted_xps)

            for xp in xps:
                # For each XP, apply cuts dictated by XP components
                new_data = self._apply_cut(data, xp)
                # Retrieve the variable to be histogrammed
                var = self._get_var(new_data, xp)
                # Retrieve the event weights 
                weights = self._get_weights(new_data, xp)
                # Will have n-histograms from n-paths 
                xp_to_hists[xp].append(self._make_histogram(var, weights,xp))

        # Now we sum histograms for each XP together to compute
        # the total histogram for the XP
        jobs, xps = [], []
        for xp, data in xp_to_hists.items():    
            jobs.append(dask.delayed(sum)(data)) # sum histograms from different paths
            xps.append(xp)

        return jobs, xps

    @classmethod
    def hist_wanted(cls, sample, region, observable, syst, template,):
        '''
        Method to determine if a XP is needed or not
        Args:
            sample (Sample):  Relevant sample
            region (Region):  Relevant region
            observable (Observable): Relevant observable
            syst    (Systematic): Relevant systematic 
            template (str):  Relevant template
        '''
        
        make_hist: bool = True
        make_hist &= sample_in_region(sample, region)
        make_hist &= template_in_sample(sample, template)
        
        if template == 'nom':   return make_hist
        
        make_hist &= observable_in_region(observable, region)
        make_hist &= sample_in_systematic(sample, syst)
        make_hist &= region_in_systematic(region, syst)
        
        make_hist &= observable_in_systematic(observable, syst)
        make_hist &= systematic_has_shape(syst)
        if template != "nom":   make_hist &= template_is_symm(syst, template)
        return make_hist

def _x_in_y(x, ypos, yneg):
    if ypos is None and yneg is None: return True
    elif ypos is None and yneg is not None:
        regex = "(" + ")|(".join(yneg) + ")"
        if re.match(regex, x.name) is not None:  return False
        else:   return True 
    elif ypos is not None and yneg is None:
        regex =  "(" + ")|(".join(ypos) + ")"        
        if re.match(regex, x.name) is not None:  return True
        else:   return False

def observable_in_region(observable, region):
    def check_region():
        return _x_in_y(observable, region.observables, region.excluded_observables)
    def check_obs():
        return _x_in_y(region, observable.regions, observable.excluded_regions)
    return check_region() & check_obs()

def sample_in_region(sample, region):
    return _x_in_y(sample, region.samples, region.excluded_samples )

def sample_in_systematic(sample, systematic):
    return _x_in_y(sample,  systematic.samples, systematic.excluded_samples )

def region_in_systematic(region, systematic):
    return _x_in_y(region, systematic.regions, systematic.excluded_regions )

def observable_in_systematic(observable, systematic):
    return _x_in_y(observable,  systematic.observables, systematic.excluded_observables )

def template_in_sample(sample, template):
    if sample.isdata and template != 'nom': return False
    else:   return True

def systematic_has_shape(systematic):
    if systematic.type in ['shape', "shapenorm"]:   return True
    else:   return False

def template_is_symm(systematic, template):
    if getattr(systematic, template) in (None, [None]) and systematic.symmetrize: return False
    else:   return True

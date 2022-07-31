'''
This is where manage different parts of the histogramming stage
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

        Attributes:
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
         These are defined as:
            - Variables directly requested with the Observable('variable','name') API
            - Variables required to compute new Observables (either passed as args or inferred from a string)
            - Weights column
            - Variables required to apply a region seleciton
            - Variables required to compute a weight variation
        
        These variables are encoded in `Functor` instances for each 
        Observable, Selection and WeightSyst instances, as the attribute req_vars  
        
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
        Method to summarise all the input files that need to be opened, so that
        the task manager can open each file only once and get what's needed from it. 
        The paths are constructed for each XP assuming Pythium naming system, where
        a file is defiend by a sample + dataset.
        TODO:: Support Custom inputs 
        
        Paths are gather from (In case of Pythium-like input):
            - Paths to the nominal file needed for an observable
            - Path to an alternative sample needed for an NTup systematic
            - Path to an alternative tree needed for a Tree systematic
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
                paths = [f"{path}/{sample_name}_*_{obs_dataset}.{self.ext}" for path in self.indirs]
                
                # If this is not a nominal histogram, then we may have NTuple or Tree variations
                if template != 'nom':
                    # If we have an Ntuple variation, then we want to access same dataset but different sample 
                    if isinstance(systematic, NTupSyst):
                        # User can ask to look in some other directory different from general setting
                        sys_dirs =    getattr(systematic, "where", [None])
                        sys_samples = getattr(systematic, template)
                        if sys_dirs == [None]:
                            paths = [f"{indir}/{s_samp}_*_{obs_dataset}.{self.ext}" for indir in indirs for s_samp in sys_samples]
                        else:
                            paths = [f"{s_dir}/{s_samp}_*_{obs_dataset}.{self.ext}" for s_dir in sys_dirs for s_samp in sys_samples]
                    
                    # If we have a Tree variation, then we want to access a different dataset but same sample 
                    elif (isinstance(systematic, TreeSyst)):
                        syst_dataset = getattr(systematic, template) 
                        paths = [f"{indir}/{sample_name}_*_{syst_dataset}.{self.ext}" for indir in self.indirs]

                # Glob and remove duplicates
                paths = list(set([p for path in paths for p in glob(path) if not os.path.isdir(p) ]))
                xp_to_paths[xp] = paths
               
            else:
                ## TODO:: Assume user defined (somehow?) #Custom? some supported special types? decoreator for custom?
                logger.warning("Only outputs from Pythium currently supported")
                pass

        return xp_to_paths

class _TaskManager(object):
    def __init__(self, method, sample_sel):
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
        data, _ = self.reader(inpath, list(set([vvar for v in observables for vvar in v.var ])))
        return data, _
    
    @dask.delayed
    def _merge_data(self, data_lst):
        return ak.concatenate(data_lst)

    @dask.delayed
    def _make_histogram(self, var_data, weights, xp):
        observable = xp["observable"]
        axes = observable.axes
        h = Hist(*axes, name = observable.name, storage=hist.storage.Weight())
        ## TODO:: Data rendering for masking problems
        var_arrs = []
        for field in var_data.fields:   var_arrs.append(var_data[field])
        h.fill(*var_arrs, weight = weights)
        return h

    @dask.delayed
    def sort_xps(self, xps):
        '''
        Sort the cross product order so that all new variables that do not depend on other
        new variables are computed first. This makes the creation of the variables less problematic
        and avoids need for recursion which is bad practice in dask.delayed() funcitons. 
        '''
        now, later = [], []
        for xp, _ in xps:
            observable = xp["observable"]
            builder = observable.builder
            if len( set(
                        [ crossprod["observable"].name 
                          for crossprod, _ in xps 
                          if crossprod["observable"].builder.new]).intersection(set(builder.req_vars)
                        )
                    ) !=0:
                
                later.append((xp, None))
            else:   now.append((xp, None))
        
        return now+later # in that order

    @dask.delayed
    def _create_variables(self, data, xps):
        # TODO:: Create variables for systematics?

        new_data = data
        # Loop through xp observables:
        for xp,_ in xps:
            observable = xp["observable"]
            builder = observable.builder

            # Note for ndim observables, this is currently useless
            # since we make the ND histogram by unpacking the
            # relevant N variables. 
            # TODO:: Find a way to support N-DIM array evaluation 
            # into the data table somehow then we can just retrieve it.
            
            if observable.name in data.fields:  continue
            # If user defines Osbsevable("In","Out"), they have to refer to it with "In"
            # when constructing other variables
            if len(observable.var) == 1 and not builder.new:    continue 
            new_data[observable.name] = builder.evaluate(data)

            if not isinstance(xp["observable"].weights, (str, float, int)):
                new_data['__pythweight__'] = xp["observable"].weights
        
        return new_data
    
    @dask.delayed
    def _apply_cut(self, data, xp):

        # FIXME:: Override or combine selection?
        new_data = data
        
        sample = xp["sample"]
        region = xp["region"]
        # 1st apply overall cuts
        # TODO:: What about overall cuts to apply to all histos?
        
        # 2. Apply sample cuts
        if sample.sel is not None and self.sample_sel:
            new_data = new_data[sample.sel.evaluate(new_data)]

        # 3. Apply region cuts
        new_data = new_data[region.sel.evaluate(new_data)]
        
        # TODO:: 4. Apply observable cuts

        return new_data
    
    @dask.delayed
    def _get_var(self, data, xp):
        observable = xp["observable"]
        systematic = xp["systematic"]
        # TODO:: Variable in systematic ?
        '''
        .var vs .name:
        * if grab from file:  We grabbed and saved a obs.var column, so can access that
        * if grab fron func:  obs.var == obs.name by construction (since the names from file are in args)
        # if grab from str:   obs.var == obs.name by construction (since the names from file are in string)
        '''
        var = data[observable.var]
        return var

    @dask.delayed
    def _get_weights(self, data, xp):
        #TODO:: overall weight
        weights = 1.
        if xp["sample"].isdata:    return weights
        #================ Observable weights 
        observable = xp["observable"]
        obs_weights = observable.weights

        if '__pythweight__' in data.fields:
            obs_weights = data['__pythweight__']
        
        if isinstance(obs_weights, str):
            obs_weights = data[obs_weights]
                 
        weights = weights*obs_weights
        
        #================ Systematic weights 
        systematic = xp["systematic"]
        if isinstance(systematic, WeightSyst):# and observable.ndim == 1:
            syst_weights = getattr(systematic, xp["template"])
            if isinstance(syst_weights, Functor):
                syst_weights = syst_weights.evaluate(data)
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

    def _build_tree(self, xp_paths_map, xp_vars_map):

        path_to_xp = defaultdict(list)
        vars_set = set()
        for xp, paths in xp_paths_map.items():
            for path in paths:
                # FIXME:: Assume that for a given path, all variables 
                # needed from all xps are available in the file. 
                vars_set |= set(xp_vars_map[xp])
                path_to_xp[path].append((xp, vars_set))
        
        xp_to_hists = defaultdict(list)
        for path, xps in path_to_xp.items():
            data = self._get_data(path,  list(xps[0][1]))[0]
            
            sorted_xps = self.sort_xps(xps)
            data = self._create_variables(data, sorted_xps)

            for xp_info in xps:
                xp = xp_info[0]

                # If weight is given as a numpy array or list, it is assumed
                # to have same size as events and hence can be added as a column
                # to data
                
                new_data = self._apply_cut(data, xp)
                var = self._get_var(new_data, xp)
                weights = self._get_weights(new_data, xp)
                # Will have n-histograms from n-paths 
                xp_to_hists[xp].append(self._make_histogram(var, weights,xp))

        
        jobs, xps = [], []
        for xp, data in xp_to_hists.items():    
            jobs.append(dask.delayed(sum)(data)) # sum histograms from different paths
            xps.append(xp)

        
        
        return jobs, xps

    @classmethod
    def hist_wanted(cls, sample, region, observable, syst, template, ):
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

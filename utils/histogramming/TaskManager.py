from utils.common.tools import h5py_to_ak, json_to_ak, parquet_to_ak
from utils.histogramming.objects import WeightSyst
import dask
from collections import defaultdict
from pprint import pprint
import boost_histogram as bh
import time 
import awkward as ak
from utils.common.functor import Functor
import numpy as np
import re
from utils.common.logger import ColoredLogger

logger = ColoredLogger()
class _TaskManager(object):
    def __init__(self, outdir, method):
        readers = {
                    'ak_parquet': parquet_to_ak,
                    'ak_jsob': json_to_ak,
                    'ak_h5': h5py_to_ak,
                    'uproot': NotImplementedError("Unsupported input type")
                    }
        self.reader = readers[method]
        self.outdir = outdir
    

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
        h = bh.Histogram(*axes, storage=bh.storage.Weight())
        # TODO:: Weight systematics with ndim histograms, dealing with ints/floats 
        #print(var_data, np.array(var_data) )
        #weights, var_data = np.broadcast_arrays(np.array(weights), np.array(var_data))
        ## TODO:: Data rendering for masking problems
        var_arrs = []
        for field in var_data.fields:   var_arrs.append(var_data[field])
        h.fill(*var_arrs, weight = weights)
        
        return h

    @dask.delayed
    def _create_variables(self, data, xps):
        # TODO:: Create variables for systematics?

        new_data = data
        # Loop through xp observables:
        for xp,_ in xps:
            observable = xp["observable"]
            builder = observable.builder
            if observable.builder is None:  continue
            else:
                # Build the variable according to builder and add it to data
                # Check if other new observables need to be built first before creating current observable
                later = []
                if len(set([xp["observable"].name for xp, _ in xps if xp["observable"].builder is not None]).intersection(set(builder.req_vars)))!=0:
                    later.append((xp, None))
                    continue

                new_data[observable.name] = builder.evaluate(data)

        if later != []:
            new_data = _create_variables(new_data, later, )                
        
        return new_data
    
    @dask.delayed
    def _apply_cut(self, data, xp):
        # FIXME:: Override or combine selection?
        new_data = data
        
        sample = xp["sample"]
        region = xp["region"]
        # 1st apply overall cuts
        # TODO:: What about overall cuts to apply to all histos?
      
        # then apply sample cuts

        
        if sample.sel is not None:
            new_data = new_data[sample.sel.evaluate(new_data)]

        # then apply region cuts
        new_data = new_data[region.sel.evaluate(new_data)]
        
        # TODO:: then apply observable cuts
        
        return new_data
    
    @dask.delayed
    def _get_var(self, data, xp):
        observable = xp["observable"]
        systematic = xp["systematic"]
        # TODO:: Variable in systematic ?
        # TODO:: ndim variabe
        var = data[observable.var]
        return var

    @dask.delayed
    def _get_weights(self, data, xp):
        
        #TODO:: overall weight
        weights = 1
        #================ Observable weights 
        observable = xp["observable"]
        obs_weights = observable.weights
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
        
        # elif isinstance(systematic, WeightSyst) and observable.ndim != 1:
        #     logger.error("Weight Systematics not yet supported for ndimensional histograms")
            
            
       
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
            data = self._create_variables(data, xps)
            for xp_info in xps:
                xp = xp_info[0]
                new_data = self._apply_cut(data, xp)
                var = self._get_var(new_data, xp)
                weights = self._get_weights(new_data, xp)

                xp_to_hists[xp].append(self._make_histogram(var, weights,xp))

        
        jobs = []
        for xp, data in xp_to_hists.items():    jobs.append(data)

        dask.visualize(jobs, filename=f'{self.outdir}/task_graph.png')
        
        return jobs

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
        # if region.observables is None and region.excluded_observables is None:
        #     return True
        # elif region.observables is None and region.excluded_observables is not None:
        #     temp = '(?:% s)' % '|'.join(region.excluded_observables)
        #     if re.match(temp, observable.name):  return False
        #     else:   return True 
        # elif region.observables is not None and region.excluded_observables is None:
        #     temp = '(?:% s)' % '|'.join(region.observables)
        #     if re.match(temp, observable.name):  return True
        #     else:   return False
        return _x_in_y(observable, region.observables, region.excluded_observables)
    
    def check_obs():
        # if observable.regions is None and observable.excluded_regions is None:
        #     return True
        # elif  observable.regions is None and observable.excluded_regions is not None:
        #     if region.name in observable.excluded_regions:  return False
        #     else:   return True 
        # elif  observable.regions is not None and observable.excluded_regions is None:
        #     if region.name in  observable.regions:   return True
        #     else:   return False
        return _x_in_y(region, observable.regions, observable.excluded_regions)
    
    return check_region() & check_obs()

def sample_in_region(sample, region):

    # if region.samples is None and region.excluded_samples is None:
    #     return True
    # elif region.samples is None and region.excluded_samples is not None:
    #     if sample.name in region.excluded_samples:  return False
    #     else:   return True 
    # elif region.samples is not None and region.excluded_samples is None:
    #     if sample.name in region.samples:   return True
    #     else:   return False
    return _x_in_y(sample, region.samples, region.excluded_samples )

def sample_in_systematic(sample, systematic):
    # if systematic.samples is None and systematic.excluded_samples is None:
    #     return True
    # elif systematic.samples is None and systematic.excluded_samples is not None:
    #     if sample.name in systematic.excluded_samples:  return False
    #     else:   return True 
    # elif systematic.samples is not None and systematic.excluded_samples is None:
    #     if sample.name in systematic.samples:   return True
    #     else:   return False
    return _x_in_y(sample,  systematic.samples, systematic.excluded_samples )

def region_in_systematic(region, systematic):
    # if systematic.regions is None and systematic.excluded_regions is None:
    #     return True
    # elif systematic.regions is None and systematic.excluded_regions is not None:
    #     if region.name in systematic.excluded_regions:  return False
    #     else:   return True 
    # elif systematic.regions is not None and systematic.excluded_regions is None:
    #     if region.name in systematic.regions:   return True
    #     else:   return False
    return _x_in_y(region, systematic.regions, systematic.excluded_regions )

def observable_in_systematic(observable, systematic):
    # if systematic.observables is None and systematic.excluded_observables is None:
    #     return True
    # elif systematic.observables is None and systematic.excluded_observables is not None:
    #     if observable.name in systematic.excluded_observables:  return False
    #     else:   return True 
    # elif systematic.observables is not None and systematic.excluded_observables is None:
    #     if observable.name in systematic.observables:   return True
    #     else:   return False
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
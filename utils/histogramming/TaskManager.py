from utils.common.tools import h5py_to_ak, json_to_ak, parquet_to_ak
import dask
from collections import defaultdict
from pprint import pprint

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
        data = self.reader(inpath, [v.name for v in observables])
        return data
    
    @dask.delayed
    def _merge_data(self, data_lst):
        return ak.concatenate(data_lst)

    @dask.delayed
    def _make_histogram(self, var_data, xp):
        observable = xp["observable"]
        axes = observable.axes
        h = bh.Histogram(*axes, storage=bh.storage.Weight())
        ## TODO:: Now to fill we need to do some data rendering
        h.fill(var_data, weight = observable.weights)
        
        return h

    @dask.delayed
    def _create_variables(self, data, xps):
        observable = xp["observable"]
        if observable.builder is None:  return data
        else:
            # Build the variable according to builder and add it to data
            pass
        pass
    
    @dask.delayed
    def _apply_cut(self, data, xp):
        # What about overall cuts to apply to all histos?
        pass
    
    @dask.delayed
    def _get_var(self, data, xp):
        pass

    @dask.delayed
    def _get_weights(self, data, xp):
        pass

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
            data = self._get_data(path, list(xps[0][1]))
            data = self._create_variables(data, xps)
            for xp_info in xps:
                xp = xp_info[0]
                #data = self._create_variables(data, xp) ## Or maybe create all new vars first incl ones for cuts
                data = self._apply_cut(data, xp)
                var = self._get_var(data, xp)
                weights = self._get_weights(data, xp)

                xp_to_hists[xp].append(self._make_histogram(var ,xp))

        # xp_to_merged_data = {}
        # for xp, data_lst in xp_to_data.items():
        #     xp_to_merged_data[xp] = self._merge_data(data_lst)
        
        jobs = []
        for xp, data in xp_to_hists.items():
            jobs.append(data)
        
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
        make_hist &= systematic_has_shape(syst)
        if template != "nom":   make_hist &= template_is_symm(syst, template)
        return make_hist

def observable_in_region(observable, region):
    def check_region():
        if region.observables is None and region.excluded_observables is None:
            return True
        elif region.observables is None and region.excluded_observables is not None:
            if observable.name in region.excluded_observables:  return False
            else:   return True 
        elif region.observables is not None and region.excluded_observables is None:
            if observable.name in region.observables:   return True
            else:   return False
    
    def check_obs():
        if observable.regions is None and observable.excluded_regions is None:
            return True
        elif  observable.regions is None and observable.excluded_regions is not None:
            if region.name in observable.excluded_regions:  return False
            else:   return True 
        elif  observable.regions is not None and observable.excluded_regions is None:
            if region.name in  observable.regions:   return True
            else:   return False
    
    return check_region() & check_obs()

def sample_in_region(sample, region):

    if region.samples is None and region.excluded_samples is None:
        return True
    elif region.samples is None and region.excluded_samples is not None:
        if sample.name in region.excluded_samples:  return False
        else:   return True 
    elif region.samples is not None and region.excluded_samples is None:
        if sample.name in region.samples:   return True
        else:   return False

def sample_in_systematic(sample, systematic):
    if systematic.samples is None and systematic.excluded_samples is None:
        return True
    elif systematic.samples is None and systematic.excluded_samples is not None:
        if sample.name in systematic.excluded_samples:  return False
        else:   return True 
    elif systematic.samples is not None and systematic.excluded_samples is None:
        if sample.name in systematic.samples:   return True
        else:   return False

def region_in_systematic(region, systematic):
    if systematic.regions is None and systematic.excluded_regions is None:
        return True
    elif systematic.regions is None and systematic.excluded_regions is not None:
        if region.name in systematic.excluded_regions:  return False
        else:   return True 
    elif systematic.regions is not None and systematic.excluded_regions is None:
        if region.name in systematic.regions:   return True
        else:   return False
    
def template_in_sample(sample, template):
    if sample.isdata and template != 'nom': return False
    else:   return True

def systematic_has_shape(systematic):
    if systematic.type in ['shape', "shapenorm"]:   return True
    else:   return False

def template_is_symm(systematic, template):
    if getattr(systematic, template) in (None, [None]) and systematic.symmetrize: return False
    else:   return True
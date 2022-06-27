# ========= pythium tools
from utils.common.selection import Selection
from utils.common.samples import Sample
from utils.common.branches import Branch
from utils.common.logger import ColoredLogger
from utils.common.tools import Evaluator
# ========= type hinting
from typing import Optional, Union, Type, TypeVar
from beartype.typing import List, Callable, Dict
from beartype import beartype
# ========= scikit
import numpy as np
import boost_histogram as bh

class CrossProduct(object):
    def __init__(self, sample, region, obs, syst, template, ):
        self._xp = (sample, region, obs, syst, template)
    def __getitem__(self, item):    
        if item == 'sample':
            return self._xp[0]
        elif item == 'region':
            return self._xp[1]
        elif item == 'observable':
            return self._xp[2]
        elif item == 'systematic':
            return self._xp[3]
        elif item == 'template':
            return self._xp[4]
        elif type(item) == type(int):
            try:    return self._xp[item]
            except IndexError:  raise IndexError(f"Index {item} out of range for CrossProduct object")
        else:
            raise TypeError("CrossProduct object can be accessed by integers or one of following keys (sample, region, obserbale, systematic, template)")
    def __iter__(self):
        return iter(self._xp)

class _Binning(object):
    '''
    The parent binning class

    Attributes:
        binning: 
            The `np.array` that defines the bin edges
        axis:
            The number of the axis defined by this binning.
            0: x-axis, 1: y-axis. 
    '''
    @beartype
    def __init__(self, binning: Union[list[float], np.ndarray], axis: Optional[int] = None):
        self.binning = np.array(binning)
        self.axis = axis

class VarBin(_Binning):
    '''
    Inherits from :py:class:`utils.histogramming.objects._Binning`
    '''
    @beartype
    def __init__(self, binning: Union[list[float], np.ndarray], axis: Optional[int] = None):
        super(VarBin, self).__init__(binning, axis = axis)
    
class RegBin(_Binning):
    '''
    Inherits from :py:class:`utils.histogramming.objects._Binning` but constructs
    uniform binning between given limits
    
    Attributes:
        low: 
            The lower edge of histogram 
        high:
            The higher edge of histogram 
        nbins:
            The number of bins to build within the low and high
    '''
    @beartype
    def __init__(self, low: Union[float,int], high: Union[float,int], nbins: int, axis: Optional[int] = None):
        self.min = low
        self.max = high
        self.nbins = nbins
        super(RegBin, self).__init__(np.linspace(self.min, self.max,self.nbins), axis = axis)

class _ObservableBuilder(object):
    TObservableBuilder = TypeVar("TObservableBuilder", bound="_ObservableBuilder")
    
    @beartype
    def __init__(self, func: Callable, args: List[Union[str, int, float, Dict, None]], *, lit_str_arg: List[str] = [], reqvars: Optional[List[str]] = None):
        self._func = func
        self._argtypes = ["VAR" if (isinstance(arg, str) and arg not in lit_str_arg) else type(arg) for arg in args]
        self._args = args
        # This should hold the awkward array name to variable mapping
        # so that the fields in the string can be retrieved from the 
        # variable. Will be set at runtime (e.g. {"data": data})
        self._vardict = {}
        self.req_vars = self._args if reqvars is None else reqvars
    
    @classmethod
    @beartype
    def fromStr(cls, string_op: str, *, vardict: Dict = {}) -> TObservableBuilder:
        
        def _eval(string, vardict):
            return Evaluator(**vardict).evaluate(string)
        
        return cls( _eval, [string_op, vardict], lit_str_arg = [string_op], reqvars = Evaluator().get_names(string_op))
    
    @property
    def func(self) -> Callable:
        return self._func
    @property
    def argtypes(self) ->   List[Union[str, int, float, Dict, None, Branch]]:
        return self._argtypes
    @property
    def args(self) ->  List[Union[str, int, float, Dict, None]]:
        return self._args
    @property
    def name(self) -> str:
        return self._name
    @property
    def vardict(self) -> str:
        return self._vardict
    
    @vardict.setter
    def vardict(self, thedict: Dict):
        self._vardict = thedict
    
    def build(self, data):
        return True



class Observable(object):
    '''
    This class defines an observable that will be retrieved from all samples entering a
    given region, and constructed with the given binning. 
    
    Attributes:
        name: 
            The name given to the observable 
        var:
            The name of the observable in the input file
        binning:
            The chosen binning for this observable
        dataset:
            The equivalent of a TTree in ROOT files. It is the parent group for
            the observable in the input file (e.g. nominal tree in a ROOT file)
        obs_build:
            An instance of :py:class:`utils.histogramming.objects._ObservableBuilder` which defines
            how to build the observable from existing data
    '''

    TObservable = TypeVar("TObservable", bound="Observable")
    @beartype
    def __init__( self, var: str, name: str, binning: Union[_Binning, List[_Binning]], 
                  dataset: str, label: Optional[str] = '', 
                  samples:Optional[List[str]] = None, 
                  weights: Union[str, np.ndarray, list[Union[int, float]]] = 1,
                  exclude_samples: Optional[List[str]] = None,
                  regions: Optional[List[str]] = None,
                  exclude_regions: Optional[List[str]] = None, *,
                  obs_build = None ):
        
        self.var = var
        self.name = name
        self.binning = binning if isinstance(binning, list) else [binning]
        self.axes = self.get_axes()
        self.label = label
        self.dataset = dataset
        self.samples = samples
        self.excluded_samples = exclude_samples
        self.regions = regions 
        self.excluded_regions = exclude_regions
        self.weights = weights
        self.builder = obs_build
        self.selection = None # TODO::
    
    @classmethod
    @beartype
    def fromFunc(cls, name: str, func: Callable, args: List[Union[str, int, float, Dict, None]], *obs_args, **obs_kwargs) -> TObservable:
        '''
        Alternative "constructor" for `utils.histogramming.objects.Observable` class which takes a function and function args 
        instrad of `var` to compute a new observable from existing data
        Args:
            name: The name to be given to the new observable
            func: The function that defines how the variable should be computed
            args: The argument to be passed to `func` to compute the observable
        Return: 
            `utils.histogramming.objects.Observable` class instance with an `utils.histogramming.objects.ObservableBuilder`
        '''
        return cls(name, name, *obs_args, **obs_kwargs, obs_build = _ObservableBuilder(func, args, ) )

    
    @classmethod
    @beartype
    def fromStr(cls, name: str, string_op: str, *obs_args, **obs_kwargs) -> TObservable:
        '''
        Alternative "constructor" for `utils.histogramming.objects.Observable` class which takes a function and function args 
        instrad of `var` to compute a new observable from existing data
        Args:
            name: The name to be given to the new observable
            string: The string that should be parsed to compute new observable
        Return: 
            `utils.histogramming.objects.Observable` class instance with an `utils.histogramming.objects._ObservableBuilder`
        '''
        return cls(name, name, *obs_args, **obs_kwargs, obs_build = _ObservableBuilder.fromStr(string_op) )
    
    def get_axes(self):
        axes = []
        for binning in self.binning:
            if isinstance(binning, RegBin):
                axis = bh.axis.Regular(binning.nbins, binning.min, binning.max)
            else:
                axis = bh.axis.Variable(binning.binning)
            axes.append(axis)
        return axes

class Region(object):
    '''
    This class defines a phase-space region object that the user will need
    Attributes:
        name: 
            The name given to the region 
        selection:
            The :py:class:`utils.common.selection.Selection` instance to be evaluated for all
            samples that enter this region 
        samples:
            The list of :py:class:`utils.common.samples.Sample` instances that should be included
            in this region 
        exclude:
            The list of :py:class:`utils.common.samples.Sample` instances that should be excluded
            from this region
    '''

    @beartype
    def __init__(
                self, name: str, 
                selection: Selection,
                title: str = None, 
                samples: Optional[List[str]] = None, 
                exclude_samples:  Optional[List[str]] = None, 
                observables: Optional[List[Observable]] = None,
                exclude_observables:  Optional[List[str]] = None,

                **kwargs):
        
        self._name = name
        self._title = title if title is not None else name
        self._sel = selection
        self._samples = samples
        self._excluded_samples = exclude_samples
        if self._samples is not None and self._exclude is not None:
            logger.error(f"Region {self._name}: Cannot provide samples and excluded samples at the same time.")
        
        self._observables = observables
        self._excluded_observables = exclude_observables

        kwargs = {k.lower(): v for k, v in kwargs.items()}
        self.mc_weight = kwargs.get("mcweight", None)
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, val):
        self._name = val

    @property
    def sel(self):
        return self._sel
    
    @sel.setter
    def sel(self, val):
        self._sel = val

    @property
    def observables(self):
        return self._observables
    
    @observables.setter
    def observables(self, val):
        self._observables = val

    @property
    def excluded_observables(self):
        return self._excluded_observables
    
    @excluded_observables.setter
    def excluded_observables(self, val):
        self._excluded_observables = val

    @property
    def samples(self):
        return self._samples
    
    @samples.setter
    def samples(self, val):
        self._samples = val

    @property
    def excluded_samples(self):
        return self._excluded_samples
    
    @excluded_samples.setter
    def excluded_samples(self, val):
        self._excluded_samples = val

class _Systematic(object):

    def __init__(self, name: str, shape_or_norm: str , 
                up = None, down = None, symmetrize = False, 
                samples: Optional[List[str]] = None, exclude_samples: Optional[List[str]] = None,
                regions: Optional[List[str]] = None, exclude_regions: Optional[List[str]] = None,
                where = None):
       
        logger = ColoredLogger()
        self.name = name
        self.up = up
        self.down = down
        self.symmetrize = symmetrize
        up_and_down =  (self.up is not None) and (self.down is not None)
        up_or_down =  (self.up is not None) or (self.down is not None)
        if not up_or_down:  logger.error(f"Systematic {self.name}: Must provide either an up or down templates")
        if up_or_down and not up_and_down and not self.symmetrize:   logger.warning(f"Systematic {self.name}: Given one-side template but not symmetrising")   
        # if up_or_down  and not up_and_down and self.symmetrize:
        #     if (self.up is not None) and (self.down is None):
        #         self.down = self.up ## Need more rigirous symm
        #     elif (self.up is None) and (self.down is not None):
        #         self.up = self.down ## Need more rigirous symm

        self.samples = samples
        self.excluded_samples = exclude_samples
        self.regions = regions
        self.excluded_regions = exclude_regions

        ## Directory to look for samples -- default used is from general_settings
        self.where = [where] if not isinstance(where, list) else where
        self.type = shape_or_norm.lower()
        if self.type not in ['shape', 'norm', 'shapenorm']:
            logger.error(f"Systematic {self.name} has invalid type {self.type}. Options are shape, norm and shapenorm")
        
class WeightSyst(_Systematic):
    pass
class NTupSys(_Systematic):
    # Up and down can be lists!!!! 
    def __init__(self, *args, **kwargs):
        super(NTupSys, self).__init__(*args, **kwargs)
        self.up = [self.up] if not isinstance(self.up, list) else [self.up]
        self.down = [self.down] if not isinstance(self.down, list) else [self.down]

class TreeSys(_Systematic):
    def __init__(self, *args, **kwargs):
        super(TreeSys, self).__init__(*args, **kwargs)

class OverallSys(_Systematic):
    def __init__(self, name, **kwargs):
        super(OverallSys, self).__init__(*name, "norm", **kwargs)

# Try to be smart -- dont read again if you will just apply a weight 

# Think re-weighting -- user should be able to give a function to reweight their observable using another
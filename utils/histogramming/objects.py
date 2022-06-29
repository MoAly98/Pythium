# ========= pythium tools
from utils.common.selection import Selection
from utils.common.samples import Sample
from utils.common.branches import Branch
from utils.common.logger import ColoredLogger
from utils.common.tools import Evaluator
from utils.common.functor import Functor
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
        self.names = (sample.name, region.name, obs.name, syst.name if syst is not None else syst, template)
    
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
    def __init__(
        self, 
        binning: Union[list[float], np.ndarray], 
        axis: Optional[int] = None
    ) -> None:

        self.binning = np.array(binning)
        self.axis = axis

class VarBin(_Binning):
    '''
    Inherits from :py:class:`utils.histogramming.objects._Binning`
    '''
    @beartype
    def __init__(
        self, 
        binning: Union[list[float], np.ndarray], 
        axis: Optional[int] = None
    ) -> None:
        
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
    def __init__(
        self, 
        low: Union[float,int], 
        high: Union[float,int], 
        nbins: int, 
        axis: Optional[int] = None
    ) -> None:

        self.min = low
        self.max = high
        self.nbins = nbins
        super(RegBin, self).__init__(np.linspace(self.min, self.max,self.nbins), axis = axis)

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
    T = TypeVar("T")
    TypeOrListOfTypes = Union[T, List[T]]
    ListOrListOfLists = Union[List[T], List[List[T]]]
    NumbersArray = Union[np.ndarray, List[Union[int, float]]]

    @beartype
    def __init__( 
        self, var: TypeOrListOfTypes[str], 
        name: str, 
        binning: TypeOrListOfTypes[_Binning], 
        dataset: str, 
        weights: TypeOrListOfTypes[Union[str, NumbersArray]] = 1.,
        label: Optional[str] = '', 
        samples: Optional[List[str]] = None, 
        exclude_samples: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        exclude_regions: Optional[List[str]] = None, 
        *,
        obs_build: Optional[TypeOrListOfTypes[Functor]] = None
    ) -> None :
        
        # Everything arrays to support ndim operations
        self.var = var if isinstance(var, list) else [var]
        self.binning = binning if isinstance(binning, list) else [binning]
        self.axes = self.get_axes()
        self.weights = weights if isinstance(weights, list) else [weights]*len(self.var)
        if isinstance(weights, (int, float)):   self.weights = weights
        h_attr = [self.var, self.binning, self.axes, self.weights]
        assert all(len(attr) == len(h_attr[0]) for attr in h_attr if (attr != self.weights and weights!=1.))
        self.ndim = len(h_attr[0])

        self.builder = obs_build
        if self.ndim != 1 and self.builder is not None:  logger.error("Building n-dim observables on the fly is not supported")
       
        self.name = name
        self.label = label
        self.dataset = dataset
        self.samples = samples
        self.excluded_samples = exclude_samples
        self.regions = regions 
        self.excluded_regions = exclude_regions
        self.selection = None # TODO::
    
    @classmethod
    @beartype
    def fromFunc(
        cls, 
        var: str, 
        func: TypeOrListOfTypes[Callable], 
        args: ListOrListOfLists[Union[str, int, float, Dict]],
        *obs_args, 
        **obs_kwargs
    ) -> TObservable:
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
        
        return cls(var, var, *obs_args, **obs_kwargs, obs_build = Functor(func, args, ) )

    
    @classmethod
    @beartype
    def fromStr(
        cls, name: str, 
        string_op: str, 
        *obs_args, 
        **obs_kwargs
    ) -> TObservable:

        '''
        Alternative "constructor" for `utils.histogramming.objects.Observable` class which takes a function and function args 
        instrad of `var` to compute a new observable from existing data
        Args:
            name: The name to be given to the new observable
            string: The string that should be parsed to compute new observable
        Return: 
            `utils.histogramming.objects.Observable` class instance with an `utils.histogramming.objects._ObservableBuilder`
        '''
        return cls(name, name, *obs_args, **obs_kwargs, obs_build = Functor.fromStr(string_op) )
    
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
        self.weights = kwargs.get("weights", 1.)
        
    @property
    def name(self):
        return self._name

    @property
    def sel(self):
        return self._sel

    @property
    def observables(self):
        return self._observables

    @property
    def excluded_observables(self):
        return self._excluded_observables
    
    @property
    def samples(self):
        return self._samples
    
    @property
    def excluded_samples(self):
        return self._excluded_samples
    
TTemplate = Union[str, Dict[str, Union[Callable,  List[Union[str, int, float, Dict, None]]]]]
class _Systematic(object):

    # Can be a string if it is a branch in data or from a string function
    # Can be Dict with keys being func and args specifying function (callable) 
    # and arguments (list) to build templates
   

    def __init__(
        self, 
        name: str, 
        shape_or_norm: str , 
        up: TTemplate = None, 
        down: TTemplate = None, 
        where: str = None,
        symmetrize: bool = False, 
        samples: Optional[List[str]] = None, 
        exclude_samples: Optional[List[str]] = None,
        regions: Optional[List[str]] = None, 
        exclude_regions: Optional[List[str]] = None,
        observables: Optional[List[str]]  = None, 
        exclude_observables: Optional[List[str]] = None, 
    ) -> None:
       
        logger = ColoredLogger()
        self.name = name
        self.up = up
        self.down = down
        self.symmetrize = symmetrize
        up_and_down =  (self.up is not None) and (self.down is not None)
        up_or_down =  (self.up is not None) or (self.down is not None)
        if not up_or_down:  logger.error(f"Systematic {self.name}: Must provide either an up or down templates")
        if up_or_down and not up_and_down and not self.symmetrize:   logger.warning(f"Systematic {self.name}: Given one-side template but not symmetrising")   

        self.samples = samples
        self.excluded_samples = exclude_samples
        self.regions = regions
        self.excluded_regions = exclude_regions
        self.observables =  observables
        self.excluded_observables = exclude_observables

        ## Directory to look for samples -- default used is from general_settings
        self.where = [where] if not isinstance(where, list) else where
        self.type = shape_or_norm.lower()
        if self.type not in ['shape', 'norm', 'shapenorm']:
            logger.error(f"Systematic {self.name} has invalid type {self.type}. Options are shape, norm and shapenorm")
        
class WeightSyst(_Systematic):
    
    TWeightSyst = TypeVar("TWeightSyst", bound="WeightSyst")

    def __init__(self, *args, **kwargs):
        super(WeightSyst, self).__init__(*args, **kwargs)


    @classmethod
    @beartype
    def fromFunc(
        cls, 
        name: str, 
        shape_or_norm: str, 
        up: Optional[TTemplate] = None, 
        down: Optional[TTemplate] = None, 
        *sys_args, 
        **sys_kwargs
    ) -> TWeightSyst:
        
        '''
        Alternative "constructor" for `utils.histogramming.objects.WeightSyst` class which takes a function and function args 
        instrad of `var` to compute a new observable from existing data
        Args:
            name: The name to be given to the new observable
            func: The function that defines how the variable should be computed
            args: The argument to be passed to `func` to compute the observable
        Return: 
            `utils.histogramming.objects.WeightSyst` class instance with an `utils.histogramming.functor.Functor`
        '''
        if up is not None:   up = Functor(up["func"], up["args"],)
        if down is not None:  down = Functor(down["func"], down["args"],)
        
        return cls(name, shape_or_norm, up, down, *sys_args, **sys_kwargs)

    
    @classmethod
    @beartype
    def fromStr(
        cls, 
        name: str, 
        shape_or_norm: str, 
        up: Optional[str], 
        down: Optional[str], 
        *sys_args, 
        **sys_kwargs
    ) -> TWeightSyst:

        '''
        Alternative "constructor" for `utils.histogramming.objects.WeightSyst` class which takes a function and function args 
        instead of `var` to compute a new weight from existing data
        Args:
            name: The name to be given to the new observable
            string: The string that should be parsed to compute new observable
        Return: 
            `utils.histogramming.objects.WeightSyst` class instance with an `utils.common.functor.Functor`
        '''
        if up is not None:   up = Functor.fromStr(up)
        if down is not None:  down = Functor.fromStr(down)
        return cls(name, shape_or_norm, up, down, *sys_args, **sys_kwargs )


class NTupSyst(_Systematic):
    def __init__(self, *args, **kwargs):
        super(NTupSyst, self).__init__(*args, **kwargs)
        self.up = [self.up] if not isinstance(self.up, list) else [self.up]
        self.down = [self.down] if not isinstance(self.down, list) else [self.down]

class TreeSyst(_Systematic):
    def __init__(self, *args, **kwargs):
        super(TreeSyst, self).__init__(*args, **kwargs)

class OverallSyst(_Systematic):
    def __init__(self, name, **kwargs):
        super(OverallSys, self).__init__(name, "norm", **kwargs)

# Try to be smart -- dont read again if you will just apply a weight 

# Think re-weighting -- user should be able to give a function to reweight their observable using another
# ========= type hinting
from typing import Optional, Union, Type, TypeVar
from beartype.typing import List, Callable, Dict
from beartype import beartype
# ========= scikit
import numpy as np
'''
The `pythium.histogramming.objects.CrossProduct` is used in the back-end to improve
quality of code. 
'''

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
        binning: Union[List[float], np.ndarray], 
        axis: Optional[int] = None
    ) -> None:

        self.binning = np.array(binning)
        self.axis = axis

class VarBin(_Binning):
    '''
    Inherits from :py:class:`pythium.histogramming.objects._Binning`
    '''
    @beartype
    def __init__(
        self, 
        binning: Union[List[float], np.ndarray], 
        axis: Optional[int] = None
    ) -> None:
        
        super(VarBin, self).__init__(binning, axis = axis)
    
class RegBin(_Binning):
    '''
    Inherits from :py:class:`pythium.histogramming.objects._Binning` but constructs
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
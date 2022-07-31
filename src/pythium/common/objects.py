
# ========= type hinting
from typing import Optional, Union, Type, TypeVar
from beartype.typing import List, Callable, Dict
from beartype import beartype
from pythium.common.functor import Functor
from pathlib import Path

class Sample(object):
    def __init__(self, name, tag, variables, where = None, selec = None, isdata = False, files = None):
        self._name = name
        self._tag = tag if isinstance(tag, list) else [tag]
        
        if where is not None:
            self._location = [Path(direc) for direc in where] if isinstance(where, list) else [Path(where)]
        else:   self._location = where
        
        self._variables = variables
        self.selec = selec
        self._isdata = isdata
        self._data = None
        self.pythfiles = files
    
    @property
    def name(self: "Sample")-> str :
        return self._name
    
    @property
    def sel(self: "Sample")-> str :
        return self.selec

    @property
    def variables(self: "Sample")->Dict[str, List["Branch"]] :
        return self._variables
    
    @property 
    def location(self: "Sample")->Path:
        return self._location

    @property
    def tag(self:"Sample")->str:
        return self._tag

    @property
    def data(self:"Sample"):
        return self._data

    @data.setter
    def data(self:"Sample", val: dict):
        self._data = val
    
    @property
    def isdata(self:"Sample"):
        return self._isdata

    @isdata.setter
    def isdata(self:"Sample", val: bool):
        self._isdata = isdata

class Variable(object):
    
    TVariable = TypeVar("TVariable", bound="Variable")
    T = TypeVar("T")
    TypeOrListOfTypes = Union[T, List[T]]
    ListOrListOfLists = Union[List[T], List[List[T]]]
    
    def __init__(
        self, 
        name: str, 
        var: str, 
        datasets: List[str] = None,
        isprop: Optional[bool] = False, 
        *, 
        var_build: Optional[TypeOrListOfTypes[Functor]] = None, 
        **kwargs
    ):
        self._name = name
        self._var = var
        self._datasets = datasets
        self.builder = var_build
        if self.builder is None:   self.builder = Functor(lambda arg: arg, self._var, reqvars= [self._var], new = False)
        self.isprop = isprop
    
    @property
    def name(self):
        return self._name
    
    @property
    def var(self):
        return self._var
    
    @property
    def datasets(self):
        return self._datasets

    @datasets.setter
    def datasets(self, val):
        self._datasets = val
    
    @classmethod
    def fromFunc(
        cls, 
        name: str, 
        func: TypeOrListOfTypes[Callable], 
        args: ListOrListOfLists[Union[str, int, float, Dict]],
        *var_args, 
        **var_kwargs
    ) -> TVariable:
        '''
        Alternative "constructor" for :py:class:`pythium.common.objects.Variable` class which takes a function and function args 
        instead of `var` to compute a new variable from existing data

        Args:
            name: The name to be given to the new observable
            func: The function that defines how the variable should be computed
            args: The argument to be passed to `func` to compute the observable

        Return: 
            :py:class:`pythium.common.objects.Variable` class instance with an :py:class:`pythium.common.tools.Functor` instance
        '''
        
        return cls(name, name, *var_args, **var_kwargs, var_build = Functor(func, args, ) )

    @classmethod
    @beartype
    def fromStr(
        cls, 
        name: str, 
        string_op: str, 
        *var_args, 
        **var_kwargs,
    ) -> TVariable:

        '''
        Alternative "constructor" for :py:class:`pythium.common.objects.Variable` class which takes a mathematical
        operation as a string to compute new variables from exisiting data. 

        Args:
            name: The name to be given to the new observable
            string: The string that should be parsed to compute new observable

        Return: 
            :py:class:`pythium.common.objects.Variable` class instance with an :py:class:`pythium.common.tools.Functor` instance
        '''
        return cls(name, name, *var_args, **var_kwargs, var_build = Functor.fromStr(string_op) )


class Selection(Functor):

    def __init__(self, *args, **kwargs):
        super(Selection, self).__init__(*args, **kwargs)
        self._label = kwargs.get("label", None) # to print on plots


    def combined_label(self):
        combine_cuts = ''
        if self._label is None:
            return ''
        if isinstance(self._label, list):
            for cut in self._label:
                if cut!= self._label[-1]:
                    combine_cuts+=cut+'\n'
                else:
                    combine_cuts+=cut
        else: # it's a str
            combine_cuts = self._label
        return combine_cuts
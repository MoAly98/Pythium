
from utils.common.tools import Evaluator
# ========= type hinting
from typing import Optional, Union, Type, TypeVar
from beartype.typing import List, Callable, Dict
from beartype import beartype
import awkward as ak

class Functor(object):
    def __init__(self, func, args, *, list_str_arg: List[str] = [], reqvars: Optional[List[str]] = None, **kwargs):
        self._func = func
        self._args = args
        self._argtypes = ["VAR" if (isinstance(arg, str) and arg not in list_str_arg) else type(arg) for arg in args]
        self._vardict = {}
        self.req_vars = self._args if reqvars is None else reqvars
    
    @classmethod
    def fromStr(cls, string_op, label = None, *, vardict = {}):
        
        def _eval(string, vardict):
            return Evaluator(**vardict).evaluate(string)
        
        return cls(_eval, [string_op, vardict], list_str_arg = [string_op], reqvars = Evaluator().get_names(string_op), label = label)
    

    @property
    def args(self):
        return self._args
    @property
    def func(self):
        return self._func
    @property
    def label(self):
        return self._label
    @property
    def argtypes(self):
        return self._argtypes

    @property
    def vardict(self) -> str:
        return self._vardict
    @vardict.setter
    def vardict(self, thedict: Dict):
        self._vardict = thedict


    def evaluate(self, data):
        
        self.vardict = {rv: data[rv] for rv in self.req_vars}
        args = [data[arg] if self.argtypes[i] == "VAR" else arg for i, arg in enumerate(self.args)]
        if not any(type(arg) == ak.Array for arg in args) and any(arg == {} for arg in args):
            # Then I am a string constructor because no data was retrieved
            args = [self.vardict if arg == {} else arg for arg in args]
        
        return self.func(*args)
''' We create a Branch class'''
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Type
from utils.common import logger
import sys
logger = logger.ColoredLogger()


AlgType = Union[Callable[..., 'Branch'], str]
AlgArgs = Optional[List[Union[str, float, int]]]
T = TypeVar('T')
AlgArgsTypes = Optional[List[Type[T]]]

class Branch:
    def __init__(self, out_name: str, alg: AlgType, 
                 args: AlgArgs = None, args_types: AlgArgsTypes = None, 
                 isprop=False, 
                 branch_type: Optional[str] = 'on',
                 args_from: List[str] = None,
                 drop: bool = False):
        self.write_name = out_name
        self.alg = alg # Can be a string with branch name, or a function
        self.isprop = isprop
        self.alg_args = args
        self.alg_arg_types = args_types
        if (isinstance(self.alg, str) and self.isprop is True) or callable(self.alg):
            self.branch_type = 'new'
        else:
            self.branch_type = branch_type
        self.drop = drop
        self.args_from = args_from


from pythium.common.tools import Evaluator
from pythium.common.functor import Functor
# ========= type hinting
from typing import Optional, Union, Type, TypeVar
from beartype.typing import List, Callable, Dict
from beartype import beartype

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
            
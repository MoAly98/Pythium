
class Selection(object):
    def __init__(self, func, args, label = None):
        self._func = func
        self._args = args
        self._label = label # to print on plots
    
    @classmethod
    def fromStr(cls, string_op, label = None, *, vardict = {}):
        
        def _eval(string, vardict):
            return ev.Evaluator(vardict).evaluate(string)
        
        return cls(_eval, [string_op, vardict], label = label)

    @property
    def args(self):
        return self._args
    @property
    def func(self):
        return self._func
    @property
    def label(self):
        return self._label

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
            
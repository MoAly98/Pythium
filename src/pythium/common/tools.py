from collections import defaultdict
from itertools import chain
from operator import methodcaller
import h5py
import awkward as ak
import numpy as np
#import dask_awkward as dak
import types

def combine_list_of_dicts(list_of_dicts):
    # initialise defaultdict of lists
    dd = defaultdict(list)
    # iterate dictionary items
    dict_items = map(methodcaller('items'), list_of_dicts)
    for tree, df in chain.from_iterable(dict_items):
        dd[tree].append(df)
    return dd

def h5py_to_ak(infile, req_branches = None):
    with h5py.File(infile, "r") as file:
        if len(file.keys()) > 1:    raise IOError("H5 file Invalid as it contains more than one group (i.e. tree)") 
        tree = file[list(file.keys())[0]]
        
        data = ak.from_buffers(
                                ak.forms.Form.fromjson(tree.attrs["form"]),
                                tree.attrs["length"],
                                {k: np.asarray(v) for k, v in tree.items()},
                                )
        
        if req_branches is None:    req_branches = data.fields
        data = data[[f for f in req_branches]]
        cuts = tree.attrs["sel"]
    
    return data, cuts

def json_to_ak(infile, req_branches = None):
    data = ak.from_json(infile)           
    if req_branches is None:    req_branches = data.fields
    data = data[[f for f in req_branches]]
    return data, None

def parquet_to_ak(infile, req_branches = None):
    return ak.from_parquet(infile, lazy=True, columns = req_branches), None

def func_deepcopy(f, name=None):
    '''
    return a function with same code, globals, defaults, closure, and 
    name (or provide a new name)
    '''
    fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__,
        f.__defaults__, f.__closure__)
    # in case f was given attrs (note this dict is a shallow copy):
    fn.__dict__.update(f.__dict__) 
    return fn

# =============== AST Expression evaluator
import ast
import operator as op

class Evaluator(ast.NodeVisitor):
    def __init__(self, **kwargs):
        self._namespace = kwargs
        self.operators = {
                    ast.Add: op.add, 
                    ast.Sub: op.sub, 
                    ast.Mult: op.mul,
                    ast.Div: op.truediv, 
                    ast.Pow: op.pow, 
                    ast.USub: op.neg, # Unary (e.g. -1)
                    ast.Eq: op.eq,
                    ast.NotEq: op.ne,
                    ast.Lt:  op.lt,
                    ast.LtE: op.le,
                    ast.Gt: op.gt,
                    ast.GtE: op.gt,
                    ast.BitXor: op.xor,
                    ast.BitAnd: op.and_,
                    ast.BitOr: op.or_,
                    ast.And:  ast.And,
                    ast.Or: ast.Or,

                    }
    
    def visit_Name(self, node):
        return self._namespace[node.id]

    def visit_Num(self, node):
        return node.n

    def visit_NameConstant(self, node):
        return node.value
    
    def visit_Attribute(self, node):
        return getattr(self.visit(node.value), node.attr)

    def visit_UnaryOp(self, node):
        val = self.visit(node.operand)
        return self.operators[type(node.op)](val)

    def visit_BinOp(self, node):
        
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        return self.operators[type(node.op)](lhs, rhs)
    
    def visit_Compare(self, node):
        lhs = self.visit(node.left)
        comps = node.comparators

        if len(comps) == 1:
            binop = ast.BinOp(op=node.ops[0], left=node.left, right=comps[0])
            return self.visit_BinOp(binop)
        else:
            left = node.left
            values = []
            for op, comp in zip(node.ops, comps):
                new_node = ast.Compare(comparators=[comp], left=left, ops=[op])
                left = comp
                values.append(new_node)
            boolop = ast.BoolOp(op=ast.And(), values=values)
            return self.visit_BoolOp(boolop) 

    def visit_BoolOp(self, node):
        values = node.values
        if isinstance(node.op, ast.And):
            return  all(self.visit(v) for v in values)
        if isinstance(node.op, ast.Or):
            return  any(self.visit(v) for v in values)    
    
    def generic_visit(self, node):
        raise ValueError("malformed node or string: " + repr(node))

    def evaluate(self, string):
        node = ast.parse(string, mode='eval')
        return self.visit(node.body)

    def get_names(self, string):
        variables = [node.id for node in ast.walk(ast.parse(string)) if isinstance(node, ast.Name)]
        return variables
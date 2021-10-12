#!/usr/bin/env python3
def combine_dicts(*, dicts):
    from collections import defaultdict
    dd = defaultdict(list)
    if not isinstance(dicts, list) or len(dicts) < 2:
        raise ValueError(f'Invalid Argument. Make sure to supply a list of size 2 or more')
    for a_dict in dicts:
        for key, val in a_dict.items():
            dd[key] += val
    return dict(dd)


def branches_from_expr(expression):
    import ast
    parsed = ast.parse(expression)
    branches = [str(node.id)
                for node in ast.walk(parsed)
                if isinstance(node, ast.Name)]
    return branches


def indexing_from_expr(expression):
    import ast
    parsed = ast.parse(expression)
    indicies = [str(node.id)
                for node in ast.walk(parsed)
                if isinstance(node, ast.Name)]
    return indicies

def ops_from_expr(expression):
    import ast
    parsed = ast.parse(expression)
    br = ['1']
    ops = [node.op
           for node in ast.walk(parsed)
           if isinstance(node, ast.BinOp)]
    return ops


def branch_expr_to_df_expr(df_name, expression):
    import re
    branches = branches_from_expr(expression)
    slicing_expr = True 
    if len(re.findall(r'\[([0-9]+|:)\s+\,?\s+([0-9]+|:)\]', expression)) != 0:
        if len(re.findall(r'\[([0-9]+|:)\s+\,\s+([0-9]+|:)\]', expression)) != 0:
                entry = re.findall(r'\[([0-9]+|:)\s+\,\s+([0-9]+|:)\]', expression)[0][0]
                sub_entry = re.findall(r'\[([0-9]+|:)\s+\,\s+([0-9]+|:)\]', expression)[0][1]
                if entry == ':':
                    expression = f'{df_name}.loc[(slice(None), 0), :]'
                    return expression
                    # pass
                pass
    for branch in branches:
        expression = expression.replace(branch, f"{df_name}['{branch}']")
    return expression

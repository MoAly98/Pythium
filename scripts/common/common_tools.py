#!/usr/bin/env python3
def combine_dicts(*, dicts:list) -> dict:
    """
    Combining row-wise python dictionaries which have identical columns
    
    Args:
        dicts: A required keyword argument with a list of dictionaries to combine

    Returns:
        A combined dictionary

    """
    from collections import defaultdict
    dd = defaultdict(list)
    if not isinstance(dicts, list) or len(dicts) < 2:
        raise ValueError(f'Invalid Argument. Make sure to supply a list of size 2 or more')
    for a_dict in dicts:
        for key, val in a_dict.items():
            dd[key] += val
    return dict(dd)


def branches_from_expr(expression: str) -> 'list':
    """
    Function to extract branches needed to build a new branch
    
    Args:
        expression: This is the mathematical expression that defines a new branch

    Returns:
        A list of branch names needed for calculating new branch

    """
    import ast
    parsed = ast.parse(expression)
    branches = [str(node.id)
                for node in ast.walk(parsed)
                if isinstance(node, ast.Name)]
    return branches


def indexing_from_expr(expression: str) -> 'list':
    """ Get dataframe sub-indices needed for making new branch

    To save a new branch that depends on jagged branches, the name of the dataframe sub-indicies
    to be used for jagged branches is extracted from a mathematical expression
    equivalent to the one passed to :func:`~common.common_tools.branches_from_expr`
    but replaces branch names with index names. AST is used to parse the string, and any :class:`ast.Name` 
    object is considered a branch.
    

    Todo:
        * Add support to expressions including multiple jagged branches when this is used
    
    Args:
        expression: This is the mathematical expression that defines a new branch but using index names instead
                    of constiuent branch names

    Returns:
        A list of dataframe index names needed for saving the new branch

    """
    import ast
    parsed = ast.parse(expression)
    indicies = [str(node.id)
                for node in ast.walk(parsed)
                if isinstance(node, ast.Name)]
    return indicies

def ops_from_expr(expression: str) -> 'list':
    """
    Function to extract operators needed to build a new branch from a formula.
    
    Args:
        expression: This is the mathematical expression that defines a new branch

    Returns:
        A (sorted) list of operators names needed for calculating new branch 

    """
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

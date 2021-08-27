

def combine_dicts(*, dicts):
    from collections import defaultdict
    dd = defaultdict(list)
    if not isinstance(dicts, list) or len(dicts) < 2:
        raise ValueError(f'Invalid Argument. Make sure to supply a list of size 2 or more')
    for a_dict in dicts:
        for key, val in a_dict.items():
            dd[key] += val
    return dict(dd)

# dic1 = {'A':    [1, 2, 3], 'B':   [4, 5, 6], 'C':    [7, 8, 9]}
# dic2 = {'D':    ['x', 'y', 'z'], 'E':   ['l', 'm', 'n'], 'C':    [10, 11, 12]}

# dict3 = combine_dicts(dicts=[dic1, dic2])
# print(dict3)


# def get_paths(dirs, dsids, exclude=[]):
'''
        # if len(exclude) != 0:
        #   exclude_regex = '^/(?!.*('
        #   for idx, pattern in enumerate(exclude):
        #       exclude_regex += pattern
        #       if idx != len(exclude)+1:
        #           exclude_regex += '|'
        #       else:
        #           pass 
        #   exclude_regex += ')).*'
        # else:
        #   exclude_regex = ''
'''
#     from glob import glob
#     paths = []
#     for directory in dirs:
#         for dsid in dsids:

#             general_path = glob(directory + '*' + dsid + '*')
#             paths_to_keep = set(general_path)


#             n=0
#             for excluded_file in exclude:
#                 print(n)
#                 n+=1
#                 print(paths_to_keep)
#                 excluded_dir = glob(directory + '*' + excluded_file + '*')
#                 paths_to_keep -= set(excluded_dir)

#             paths_to_keep = list(paths_to_keep)
#             paths.append(paths_to_keep)
#     return paths

# dirs = ['./testdir1/', './testdir2/']
# dsids = ['12345', '67890']
# exclude = ['*p123*', '*p345*']
# paths = get_paths(dirs, dsids, exclude)
# print(paths)


# def get_branches_filter(branches_to_keep, branches_to_drop):
#     branches = []
#     positive_regex = '/('
#     for idx, branch in enumerate(branches_to_keep):
#         name = branch  # branch.name
#         if "*" in name and ".*" not in name:
#             name = name.replace("*", ".*")

#         if idx == len(branches_to_keep)-1:
#             positive_regex += name
#         else:
#             positive_regex += name + '|'
#     positive_regex += ')/i'
#     branches.append(positive_regex)

#     negative_regex = '/^((?!('
#     for idx, branch in enumerate(branches_to_drop):
#         name = branch  # branch.name
#         if "*" in name and ".*" not in name:
#             name = name.replace("*", ".*")
#         if idx == len(branches_to_drop)-1:
#             negative_regex += name
#         else:
#             negative_regex += name + '|'

#     negative_regex += ')).)*$/i'

#     branches.append(negative_regex)
#     return branches

# branches_to_keep = ['*met*', '.*foxwolfram.*']
# branches_to_drop = ['*lepton*', '.*jets.*', 'branch1']

# filtered = get_branches_filter(branches_to_keep, branches_to_drop)

# print(filtered)


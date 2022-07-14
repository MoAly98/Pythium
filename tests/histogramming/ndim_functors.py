


import awkward as ak
arr =  ak.Array({'x':[1,2,3], 'y': [4,5,6], 'z': [7,8,9]})
arrbreak = ak.Array({'x':[1,2,3], 'y': [4,5,6], 'z': [7,8,9]})

# arrbreak = arr makes arr follow arrbreak through reference.. need to do a copy or just a a new arr

func = lambda *args: args
args = [['x']]
name = 'x'
dataargs = [arr[arg] for arg in args]
newarr = func(*dataargs)

arrbreak[name] = newarr # wrong result {x: {x:1, x:2,...}} 

if name not in arr.fields:  arr[name] = newarr

print(f"Wrong array: {arrbreak}")
print(f"Correct array: {arr}")
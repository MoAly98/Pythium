import awkward as ak

def count_jagged(arr, axis=None):
    return ak.count(arr,axis=axis)

def mask(arr, mask=None):
    return ak.mask(arr, mask=mask)

def flatten(arr, axis):
    return ak.flatten(arr, axis=axis)
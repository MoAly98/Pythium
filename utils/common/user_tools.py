import awkward as ak
import vector

def count_jagged(arr, axis=None):
    return ak.count(arr,axis=axis)

def mask(arr, mask=None):
    return ak.mask(arr, mask=mask)

def flatten(arr, axis):
    return ak.flatten(arr, axis=axis)

def momentum_4d(px,py,pz,mass):
    vector.register_awkward()
    return ak.zip({"px":px,"py":py,"pz":pz,"mass":mass},with_name="Momentum4D")

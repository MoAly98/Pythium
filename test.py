import awkward as ak
import numpy as np
import vector

from misc.lorentz_functions import Vector3

px = ak.Array([1.,2.,3.,4.,5.])
py = ak.Array([2.,4.,6.,8.,10.])
pz = ak.Array([1.,-1.,2.,-2.,0.])
m = ak.Array([.1,.1,.1,.1,.1])

akarr = vector.zip({"px":px,"py":py,"pz":pz,"mass":m})
print(type(akarr))

vector.register_awkward()
akarr2=ak.zip({"px":px,"py":py,"pz":pz,"mass":m},with_name="Momentum4D")
print(type(akarr2))

tmp = ak.zip({"px":px,"py":py,"pz":pz,"mass":m})
akarr3 = vector.awk(tmp)
print(type(akarr3))
print(getattr(akarr3,'mass'))

akarr4 = Vector3(akarr3)
print(type(akarr4))
print(akarr4)

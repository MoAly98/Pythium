import awkward as ak
import numpy as np
from skhep.math.vectors import LorentzVector
from vector import awkward
import misc.lorentz_functions as VF

px = np.array([1.,2.,3.,4.,5.])
py = np.array([2.,4.,6.,8.,10.])
pz = np.array([1.,-1.,2.,-2.,0.])
e = np.array([.1,.1,.1,.1,.1])

arr = []
nparr = np.empty([0,4])
for i in range(len(px)):
    p = VF.P4(px[i],py[i],pz[i],e[i])
    nparr = np.append(nparr,[p], axis=0)
    arr.append(p)

print(arr)
print(type(arr[0]))
awkarr = ak.Array(arr)
print(awkarr)
print(type(awkarr[0]))
print(nparr)
print((nparr[0]))


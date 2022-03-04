import numpy as np
import awkward as ak
import vector

from utils.common.branches import T

PROTON_MASS = 0.938 #GeV
SQRT_S = 13e3 #GeV

def Vector3(p4):
    return ak.zip({"px":p4.x,"py":p4.y,"pz":p4.z},with_name="Momentum3D")

def Unit3(p4):
    return Vector3(p4).unit()

def Gamma(beta):
    return pow(1-beta.dot(beta),-0.5)

def CoMVector(*plist):
    p_com = vector.obj(px=0,py=0,pz=0,energy=0)
    for p4 in plist:
        p_com = p_com + p4
    return p_com

def BetaV3(*plist):
    p_com = CoMVector(plist)
    return p_com.to_beta3()*(-1)

def DeltaEta(p1,p2):
    return p2.eta - p1.eta

def DeltaPhi(p1,p2):
    deltaphi = p2.phi - p1.phi
    if deltaphi > np.pi : deltaphi = deltaphi - 2*np.pi
    elif deltaphi < -np.pi: deltaphi = deltaphi + 2*np.pi
    return deltaphi

def DeltaR(p1,p2):
    return pow(DeltaEta(p1,p2)**2 + DeltaPhi(p1,p2)**2,0.5)

def InvMass(*plist):
    p_com = CoMVector(plist)
    return p_com.mass

def Et(*plist):
    et = 0
    for p in plist: et += p.pt
    return et

def ProtonP4(posZ=True,beta=None):
    sign = +1 if posZ else -1
    p4 = vector.obj(px=0,py=0,pz=sign*SQRT_S/2,mass=PROTON_MASS)
    if beta:
        p4 = p4.boost(beta)
    return p4

def Cos(q1,q2):
    return q1.dot(q2) / (abs(q1)*abs(q2))

def TripleProd(q1,q2,q3):
    return q1.dot(q2.cross(q3))

def TripleProdSign(q1,q2,q3,beta=None):
  tripleprod = TripleProd(q1,q2,q3,False,beta)
  if tripleprod == 0: return tripleprod
  return tripleprod/abs(tripleprod)

def BoostMultiple(*plist,beta):
    return [p.boost(beta) for p in plist]



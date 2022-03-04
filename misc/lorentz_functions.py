import numpy as np
import awkward as ak
import vector

from Pythium.utils.common.branches import T

vector.register_awkward()

PROTON_MASS = 0.938 #GeV
SQRT_S = 13e3 #GeV

def Vector4D(px,py,pz,E):
    return ak.zip({"px":px,"py":py,"pz":pz,"E":E},with_name="Momentum4D")

def Vector3(p4):
    return ak.zip({"px":p4.x,"py":p4.y,"pz":p4.z})

def Gamma(beta):
    return pow(1-beta.dot(beta),-0.5)

def Pt(p4):
    return p4.pt

def Eta(p4):
    return p4.eta

def Phi(p4):
    return p4.phi

def CoMVector(*plist):
    p_com = vector.obj(px=0,py=0,pz=0,energy=0)
    for p4 in plist:
        p_com = p_com + p4
    return p_com

def BetaV3(p4):
    return p4.to_beta3()*(-1)

def DeltaEta(p1,p2):
    return Eta(p2) - Eta(p1)

def DeltaPhi(p1,p2):
    deltaphi = Phi(p2) - Phi(p1)
    if deltaphi > np.pi : deltaphi = deltaphi - 2*np.pi
    elif deltaphi < -np.pi: deltaphi = deltaphi + 2*np.pi
    return deltaphi

def DeltaR(p1,p2):
    return pow(DeltaEta(p1,p2)**2 + DeltaPhi(p1,p2)**2,0.5)

def InvMass(*plist):
    p_com = CoMVector(plist)
    return p_com.mass

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

def BoostMultiple(*plist,beta):
    return [p.boost(beta) for p in plist]

def TTHVars(p1,p2,beta=None):
    qp1 = (Vector3(ProtonP4(True,beta))).unit()
    qp2 = (Vector3(ProtonP4(False,beta))).unit()
    if beta:
        p1 = p1.boost(beta)
        p2 = p2.boost(beta)
    q1 = (Vector3(p1)).unit()
    q2 = (Vector3(p2)).unit()

    b1 = Cos(q1.cross(qp1),q2.cross(qp1))
    b2 = (q1.Cross(qp1)).dot(q2.cross(qp1))
    b3x = q1.x()*q2.x()/(abs(q1.cross(qp1)*abs(q2.cross(qp2))))
    b4 = (q1.dot(qp1))*(q2.dot(qp2))
    b5 = TripleProd(qp1,q1,q2)
    b6 = TripleProd(qp1,q1,q2)/(abs(q1.cross(qp1))*abs(q2.cross(qp2)))
    b7 = TripleProd(qp1,q1,q2)/abs(q1.cross(q2))
    b8 = (qp1.Cross(qp2)).dot(p1.Cross(p2))


def PhiC(p1,p2,pH):
    beta = BetaV3(pH)
    qp1 = (Vector3(ProtonP4(True,beta))).unit()
    qp2 = (Vector3(ProtonP4(False,beta))).unit()
    p1 = p1.boost(beta)
    p2 = p2.boost(beta)
    q1 = (Vector3(p1)).unit()
    q2 = (Vector3(p2)).unit()
    phic = np.arccos(Cos(q1.Cross(q2),qp1.Cross(qp2)))/np.pi



import numpy as np
from skhep.math.vectors import Vector3D, LorentzVector

PROTON_MASS = 0.938 #GeV
SQRT_S = 13e3 #GeV

def P4(px,py,pz,E):
    p = LorentzVector()
    p.setpxpypze(px,py,pz,E)
    print(p)
    return p

def Gamma(beta):
    return pow(1-beta*beta,-0.5)

def Pt(p4):
    return p4.pt()

def Eta(p4):
    return p4.eta()

def Phi(p4):
    return p4.phi()

def CoMVector(*plist):
    p_com = LorentzVector()
    for p4 in plist:
        p_com += p4
    return p_com

def Beta(p4):
    return p4.boostvector()*(-1)

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
    return p_com.m()

def ProtonP4(posZ=True,beta=None):
    sign = +1 if posZ else -1
    p4 = LorentzVector()
    p4.setpxpypzm(0.,0.,sign*SQRT_S/2,PROTON_MASS)
    if beta:
        p4 = p4.boost(beta)
    return p4

def Cos(q1,q2):
    return q1*q2 / (abs(q1)*abs(q2))

def TripleProd(q1,q2,q3):
    return q1*(q2.cross(q3))

def TTHVars(p1,p2,beta=None):
    pp1 = (ProtonP4(True,beta)).vector()
    pp2 = (ProtonP4(False,beta)).vector()
    if beta:
        p1 = p1.boost(beta)
        p2 = p2.boost(beta)
    qp1 = pp1.unit()
    qp2 = pp2.unit()
    q1 = (p1.vector()).unit()
    q2 = (p2.vector()).unit()

    b1 = Cos(q1.cross(qp1),q2.cross(qp1))
    b2 = (q1.Cross(qp1))*(q2.cross(qp1))
    b3x = q1.x()*q2.x()/(abs(q1.cross(qp1)*abs(q2.cross(qp2))))
    b4 = (q1*qp1)*(q2*qp2)
    b5 = TripleProd(qp1,q1,q2)
    b6 = TripleProd(qp1,q1,q2)/(abs(q1.cross(qp1))*abs(q2.cross(qp2)))
    b7 = TripleProd(qp1,q1,q2)/abs(q1.cross(q2))
    b8 = (qp1.Cross(qp2))*(p1.Cross(p2))
    phic = np.arccos(Cos(p1.Cross(p2),qp1.Cross(qp2)))/np.pi



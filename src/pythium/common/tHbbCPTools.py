from pythium.common.user_tools import *

def unpack_samples(sample_info,flist):
    for group in sample_info.keys():
        for sample in sample_info[group].keys():
            info =sample_info[group][sample]
            files = []
            for container in info['containers']:
                with open(f'{flist}/{container}','r') as file:
                    lines = [line.strip() for line in file.readlines()]
                    lines = [line.replace('davs:','root:').replace('.uk:443/dpm','.uk//dpm') for line in lines]
                    files += lines
            sample_info[group][sample]['files'] = files
    return sample_info

def leading_particle(particle):
    return particle[ak.argmax(particle.pt,axis=-1,keepdims=True)][:,0]

def dxbb(pH,pT,pQ,f):
    return np.log(pH/(f*pT + (1-f)*pQ))

def overlap_removal(p1, p2, dR):
    event = ak.zip({
        'p1':p1,
        'p2':p2
        })
    return ak.any(DeltaR(event.p1,event.p2)>=dR,axis = -1)

def overlap(p1, p2, dR):
    event = ak.zip({
        'p1':p1,
        'p2':p2
    })
    return (DeltaR(event.p1,event.p2)<=dR)

def momentum_PtEtaPhiE(pt,eta,phi,e):
    px = pt*np.cos(phi)
    py = pt*np.sin(phi)
    pz = pt*np.sinh(eta)
    m  = np.nan_to_num(np.sqrt(pow(e,2) - (pow(px,2)+pow(py,2)+pow(pz,2))))
    return momentum_4d(px,py,pz,m)





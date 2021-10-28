import uproot4
import pandas as pd

def get_weight(sample, dsid, xsec_file='sample_xsections_newvars.txt', nevt_file='data/weights_dijet.root'):
    '''
    Function which derives the sample normalisation
    Special consideration for selecting where the denominator comes from.
    Inputs:
        sample -> str: Name of sample (used to identify the MC campaign)
        dsid   -> int: DSID of sample (used to check if JZX slice dijet sample)
        xsec_file -> str: CSV file with [dsid filt efficency xsec shower algorithm]
        nevt_file -> str: Path of root file containing total events (weighted or not) for denominator
    Return:
        float: (Lumi)*(Cross-section)*(Filter efficiency)/(Total weighted events)
    '''
    xsec_file = pd.read_csv(xsec_file, names=['dsid', 'filt', 'xsec', 'shower'], header=None, delimiter=' ')

    for array in uproot4.iterate(nevt_file+':sumWeights', library='pd'):
        nevt_file = array

    jzx_slice = list(range(364700,364713)) + \
                list(range(364902,364910)) + \
                list(range(364922,364930)) + \
                list(range(364681,364686)) + \
                list(range(364690,364695)) + \
                list(range(364443,364455)) + \
                list(range(426131,426143))
    mc = 1 if 'mc16a' in sample else 2 if 'mc16d' in sample else 3 if 'mc16e' in sample else -1
    dsid = int(dsid)
    if 'dijet' in sample:
        if not dsid in jzx_slice:
            nevts = float(nevt_file[(nevt_file['dsid']==dsid) & (nevt_file['Type']==mc)]['totalEvents'])
        elif dsid in jzx_slice:
            try:
                nevts = float(nevt_file[(nevt_file['dsid']==dsid) & (nevt_file['Type']==mc)]['totalEventsWeighted'])
            except:
                nevts = float(nevt_file[(nevt_file['dsid']==dsid) & (nevt_file['Type']==3 )]['totalEventsWeighted'])
    else:
        nevts = float(nevt_file[(nevt_file['dsid']==dsid) & (nevt_file['Type']==mc)]['totalEventsWeighted'])
    xsec = float(xsec_file[xsec_file['dsid']==dsid]['xsec']) * 1e6
    filt = float(xsec_file[xsec_file['dsid']==dsid]['filt'])
    lumi = 36.2 if mc is 1 else 40.5 if mc is 2 else 58.5 if mc is 3 else 1.0
    return xsec * filt / nevts * lumi



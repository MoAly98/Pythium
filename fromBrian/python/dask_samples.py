import os, sys
import uproot4
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
import matplotlib.colors as colors
import hist
from hist import Hist
import dask_histogram as dh
import dask.dataframe as dd
from grid.samples_ufo_newvars import samples_DXAOD
from functools import reduce
from termcolor import colored, cprint
from itertools import repeat, product
import multiprocessing as mp
from collections.abc import Iterable

global FILES
global TAGGERS

TAGGERS = ['dnn_cont_50', 'dnn_cont_80', 'dnn_incl_50', 'dnn_incl_80']

def add_hists(a, b):
    '''
    Simple helper function for adding together histos
    '''
    if not a:
        if b:
            return b
        else:
            return False
    else:
        if b:
            return a + b
        else:
            return a

def clean(x):
    return list(filter(bool,x))

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

def find_file(kws, folder):
    '''
    Helper function which uses filters to select samples
    Inputs
        - kws -> list[str]: List of keywords to search for
        - folder -> str: Folder path
    Return:
        list[str]: List of files matching keywords
    '''
    files_out = []
    for root, dir, files in os.walk(folder):
        for file in files:
            if all(map(lambda x: x in file, kws)):
                files_out.append(file)
    return files_out

def load_formulas(path='/cvmfs/atlas.cern.ch/repo/sw/database/GroupData/BoostedJetTaggers/JSSWTopTaggerDNN/Rel21/UFO_tests/'):
    '''
    Load dictionary of splices interpreted from the tagger configs
    Inputs:
        - path -> str: Path with config files for taggers
    Return:
        formulas -> {lambda}: Dictionary structured as dict[tagger] of splices
    '''
    config = {
        'dnn_cont_50': 'DNNTagger_AntiKt10UFOSD_TopContained50_TauRatios_Oct30.dat',
        'dnn_cont_80': 'DNNTagger_AntiKt10UFOSD_TopContained80_TauRatios_Oct30.dat',
        'dnn_incl_50': 'DNNTagger_AntiKt10UFOSD_TopInclusive50_TauRatios_Oct30.dat',
        'dnn_incl_80': 'DNNTagger_AntiKt10UFOSD_TopInclusive80_TauRatios_Oct30.dat',
    }

    formulas = {}
    for name, f in config.items():
        for x in open(path+f).readlines():
            continue
        formula = x.strip().split(' ')[1]
        formula = formula.replace('TMath::Power(x,', '(x**')
        exec('formulas[name] = lambda x: '+formula)
    return formulas

def get_sample_histos(files, ax, name, debug=False, parallel=True):
    '''
    Create dictionaries of histograms, summing up the individual dsids
    One dictionary for passing/failing histos
    Inputs:
        - ax       -> hist.axis: hist axis object
        - vname    -> str: Ntuple branch name for variable
        - debug    -> bool: Debug mode
        - parallel -> bool: Enable parallelisation (default on)
    Return:
        pass -> {hist}: Dictionary of hists with dict[sample][tag] structure
        fail -> [str]: List of broken samples
    '''
    hists = {}
    cprint("Loading histos:", 'white', attrs=['bold'])
    dsids = list(files.keys())
    if isinstance(ax, Iterable):
        for n in name:
            hists[n] = {}
        _vars = zip(ax, name)
    else:
        hists[name] = {}
        _vars = zip([ax], [name])
    global FILES
    FILES = files
    if parallel:
        cprint('Parallelising', 'blue', attrs=['bold',])
        combs = list(product(_vars, dsids))
        _vars, dsids = zip(*combs)
        ax, names = zip(*_vars)
        pargs = list(zip(dsids, ax, names, repeat([True])))
        with mp.Pool(mp.cpu_count()) as pool:
            res = pool.starmap_async(make_histos, pargs)
            pool.close()
            pool.join()
        results = [x for x in res.get()]
        for i, arg in enumerate(pargs):
            dsid, _, vname, _ = arg
            hists[vname][dsid] = results[i]
    else:
        for ax, name in _vars:
            for dsid in dsids:
                hists[name][dsid] = make_histos(dsid, ax, name, debug)
    return hists

def reduce_histos(hists, sample):
    global TAGGERS
    for vname, _hists in hists.items():
        for dsid, _hist in _hists.items():
            if not 'data' in sample:
                weight  = get_weight(sample, int(dsid))
                for key in TAGGERS+['all']:
                    if _hist:
                        _hist[key] *= weight

        # Sort samples
        fnames = samples_DXAOD[sample]
        dsids = [x for x in hists[vname].keys() if hists[vname][x]]
        for tag in TAGGERS+['all']:
            hists_dsid = [hists[vname][x][tag] for x in dsids]
            hists_dsid = clean(hists_dsid)
            try:
                hists[vname][tag] = reduce(add_hists, hists_dsid)
            except:
                hists[vname][tag] = False
        for dsid in dsids:
            del hists[vname][dsid]
    global FILES
    del FILES
    return hists

def load_files(sample, folder, vnames=False, filt=[], debug=False):
    if debug:
        cprint('Colour key:', 'blue')
        cprint('File successfully processed', 'green')
        cprint('Problem with opening file', 'red', attrs=['bold'])
        cprint('Specific DSID/mc is missing from folder '+folder, 'magenta', attrs=['bold'])
    fnames = samples_DXAOD[sample]
    all_f = 0
    cprint('Loading '+sample, 'blue')
    fail = []
    broken = []
    files = {}
    for fname in fnames:
        dsid = fname.split('.')[1]
        tags = fname.split('.')[-1]
        real_name = find_file([dsid, tags, 'dijet']+filt, folder=folder)
        for r in real_name:
            all_f += 1
        files[dsid] = []
        if not real_name:
            cprint(fname, 'magenta', attrs = ['bold'])
            fail.append(fname)
            continue
        for pkl in real_name:
            _broken = []
            try:
                cols = ['rljet_m_comb[:,0]', 'rljet_topTag_DNN20_TausRatio_qqb_score', 'rljet_topTag_DNN20_TausRatio_inclusive_score']
                if vnames:
                    cols += vnames
                if not 'data' in sample:
                    cols += ['weight_mc', 'weight_pileup']
                files[dsid].append(pd.read_pickle(folder+pkl)[cols])
            except Exception as e:
                cprint(fname, 'red', attrs = ['blink'])
                cprint('\tFailed '+pkl, 'red', attrs=['bold'])
                print('\t', type(e), e)
                _broken += [(fname, e)]
                continue
            broken += _broken
        if not _broken:
            cprint(fname, 'green')
    print(all_f)
    return files, fail, broken

def make_histos(dsid, ax, vname, debug=False):
    '''
    Main function for retrieving histograms
    Inputs:
        - vname  -> str: Variable name in ntuple
        - ax     -> hist.axis: hist axis object
        - cut    -> str: pass/fail/all flag
        - debug  -> bool: Debug flag
    Return:
        hists -> {hist}: Dictionary of hist objects structured as dict[tag]
    '''
    hists = {}
    formulas = load_formulas()

    # Flatten
    global FILES
    for f in FILES[dsid]:
        tree = f.droplevel(1)
        tree = tree[tree['rljet_m_comb[:,0]']>50000.]

        # Decorate
        target = tree[vname]

        # Calculate weight
        if 'period' in dsid:
            weight = np.ones_like(tree['rljet_m_comb[:,0]'])
        else:
            weight = (tree['weight_mc']*tree['weight_pileup'])
        # Apply cuts
        h = Hist(ax, storage=hist.storage.Weight())
        #h = dh.Histogram(ax, storage=dh.storage.Double())
        h.fill(target, weight=weight)
        #h.compute()
        if 'all' in hists.keys():
            hists['all'] += h
        else:
            hists['all']  = h

        for tag, f in formulas.items():
            # Calculate weight
            if 'period' in dsid:
                weight = np.ones_like(tree['rljet_m_comb[:,0]'])
            else:
                weight = (tree['weight_mc']*tree['weight_pileup'])

            target_pass = target
            weight_pass = weight

            # Caclulate pass based on pt
            if 'cont' in tag:
                tagger = tree['rljet_topTag_DNN20_TausRatio_qqb_score']
            else:
                tagger = tree['rljet_topTag_DNN20_TausRatio_inclusive_score']
            score_cut = f
            score_cut = score_cut(tree['rljet_pt_comb']/1000.)

            # Apply cuts
            target_pass = target[tagger > score_cut]
            weight_pass = weight[tagger > score_cut]

            # Create histos
            h = Hist(ax, storage=hist.storage.Weight())
            #h = dh.Histogram(ax, storage=dh.storage.Double())
            h.fill(target_pass, weight=weight_pass)
            #h.compute()
            if tag in hists.keys():
                hists[tag] += h
            else:
                hists[tag]  = h

    return hists

#if __name__ == "__main__":
#    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_SEP/'
#    get_samples(folder, sys.argv[1], sys.argv[2], hist.axis.Variable([450,2500], name='x'), debug=True)
#


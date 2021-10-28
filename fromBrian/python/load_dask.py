import os
import sys
import dask
import uproot4
import numpy as np
import pandas as pd
import dask.dataframe as dd
import dask_histogram as dh
import multiprocessing as mp
from grid.samples_ufo_newvars import samples_DXAOD
from termcolor import colored, cprint
from itertools import product
import hist
from hist import Hist
import pickle as pkl
from dask.delayed import delayed
import dask.bag as db
from functools import reduce

global FORMULAS

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

def get_formula(formula):
    formula = formula.strip().split(':')[1:]
    formula = ':'.join(formula)
    return formula.replace('TMath::Power(x,', '(x**')

def load_formulas(path='/cvmfs/atlas.cern.ch/repo/sw/database/GroupData/BoostedJetTaggers/'):
    '''
    Load dictionary of splices interpreted from the tagger configs
    Inputs:
        - path -> str: Path with config files for taggers
    Return:
        formulas -> {lambda}: Dictionary structured as dict[tagger] of splices
    '''
    config = {
        'dnn_cont_50': 'JSSWTopTaggerDNN/Rel21/UFO_tests/DNNTagger_AntiKt10UFOSD_TopContained50_TauRatios_Oct30.dat',
        'dnn_cont_80': 'JSSWTopTaggerDNN/Rel21/UFO_tests/DNNTagger_AntiKt10UFOSD_TopContained80_TauRatios_Oct30.dat',
        'dnn_incl_50': 'JSSWTopTaggerDNN/Rel21/UFO_tests/DNNTagger_AntiKt10UFOSD_TopInclusive50_TauRatios_Oct30.dat',
        'dnn_incl_80': 'JSSWTopTaggerDNN/Rel21/UFO_tests/DNNTagger_AntiKt10UFOSD_TopInclusive80_TauRatios_Oct30.dat',
        'w_50': 'SmoothedWZTaggers/Rel21/UFO_tests/SmoothedContainedWTagger_AntiKt10VanillaSD_FixedSignalEfficiency50_July21.dat',
        'w_80': 'SmoothedWZTaggers/Rel21/UFO_tests/SmoothedContainedWTagger_AntiKt10VanillaSD_FixedSignalEfficiency80_2021May10.dat',
    }

    formulas = {}
    for name, f in config.items():
        for x in open(path+f).readlines():
            if 'dnn' in name and x.startswith('ScoreCut'):
                formula = get_formula(x)
                break
            if 'w' in name and x.startswith('MassCut'):
                if 'Low' in x:
                    m_lo = get_formula(x)
                else:
                    m_hi = get_formula(x)
            elif 'w' in name and x.startswith('D2Cut'):
                    d2 = get_formula(x)
            elif 'w' in name and x.startswith('NtrkCut'):
                    ntrk = get_formula(x)
            continue
        if 'w' in name:
            exec('formulas[name] = dict()')
            exec('formulas[name]["m_lo"] = lambda x: '+m_lo)
            exec('formulas[name]["m_hi"] = lambda x: '+m_hi)
            exec('formulas[name]["d2"]   = lambda x: '+d2)
            exec('formulas[name]["ntrk"] = lambda x: '+ntrk)
        else:
            exec('formulas[name] = lambda x: '+formula)
    return formulas


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
        real_name = find_file([dsid, tags]+filt, folder=folder)
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
                cols = ['rljet_m_comb[:,0]',
                        'rljet_topTag_DNN20_TausRatio_qqb_score',
                        'rljet_topTag_DNN20_TausRatio_inclusive_score',
                        'rljet_D2',
                        'rljet_ungroomed_ntrk500']
                if vnames:
                    for vname in vnames:
                        if '_2D_' in vname:
                            cols += vname.split('_2D_')
                        else:
                            cols.append(vname)
                if not 'data' in sample:
                    cols += ['weight_mc', 'weight_pileup']
                    if 'gammajet' in filt:
                        cols += ['weight_photonSF']
                cols = list(set(cols))
                if 'rljet_log_m_pt' in cols:
                    cols.remove('rljet_log_m_pt')
                dataset = pd.read_pickle(folder+pkl)[cols].droplevel(1)
                dataset['rljet_log_m_pt'] = np.log(dataset['rljet_m_comb[:,0]']/dataset['rljet_pt_comb'])
                files[dsid].append(dd.from_pandas(dataset, npartitions=20))
                del dataset
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

def fill_histos(trees, histo, vnames, taggers, photon):
    histos = []
    global TAGGERS
    n_trees = len(trees)
    for i in range(n_trees):
        print(i)
        histos = [fill_histo(trees[n_trees-1-i], histo, v, tag, photon) for v, tag in list(product(vnames, TAGGERS+['all']))]
        res = list(dask.compute(*histos))
        for x, r in zip(list(product(vnames, TAGGERS+['all'])), res):
            histo[x[0]][x[1]] = r
        del trees[n_trees-1-i]
    del histos
    return histo

@dask.delayed
def fill_histo(tree, histo, vname, tag, photon=False):
    '''
    Main function for retrieving histograms
    Inputs:
        - vname  -> str: Variable name in ntuple
    Return:
        hists -> {hist}: Dictionary of hist objects structured as dict[tag]
    '''
    tree = tree[tree['rljet_m_comb[:,0]']>50000.]
    if histo[vname][tag].ndim > 1:
        target = [tree[vname] for vname in vname.split('_2D_')]
    else:
        target = [tree[vname]]

    # Calculate weight
    if 'period' in dsid:
        weight = np.ones_like(tree['rljet_m_comb[:,0]'])
    else:
        weight = (tree['weight_mc']*tree['weight_pileup'])
        if photon:
            weight = (weight*tree['weight_photonSF'])

    target_pass = target
    weight_pass = weight

    # Caclulate pass based on pt
    if 'dnn' in tag:
        if 'cont' in tag:
            tagger = tree['rljet_topTag_DNN20_TausRatio_qqb_score']
        else:
            tagger = tree['rljet_topTag_DNN20_TausRatio_inclusive_score']
        score_cut = FORMULAS[tag]
        score_cut = score_cut(tree['rljet_pt_comb']/1000.)

        # Apply cuts
        target_pass = [t     [tagger > score_cut] for t in target_pass]
        weight_pass =  weight[tagger > score_cut]

    elif 'w_50' in tag or 'w_80' in tag:
        f = FORMULAS[tag]
        mass = tree['rljet_m_comb[:,0]']/1000.
        d2   = tree['rljet_D2']
        ntrk = tree['rljet_ungroomed_ntrk500']
        mlo_cut   = f['m_lo'](tree['rljet_pt_comb']/1000.)
        mhi_cut   = f['m_hi'](tree['rljet_pt_comb']/1000.)
        d2_cut    = f['d2']  (tree['rljet_pt_comb']/1000.)
        ntrk_cut  = f['ntrk'](tree['rljet_pt_comb']/1000.)

        target_pass = [t          [(d2 < d2_cut) & (mass > mlo_cut) & (mass < mhi_cut) & (ntrk < ntrk_cut)] for t in target_pass]
        weight_pass =  weight_pass[(d2 < d2_cut) & (mass > mlo_cut) & (mass < mhi_cut) & (ntrk < ntrk_cut)]

    # Create histos
    histo[vname][tag].fill(*target_pass, weight=weight_pass)

    return histo[vname][tag]

if __name__ == "__main__":
    from python.configs.vars import var_main, var_2d
    TAGGERS = ['dnn_cont_50', 'dnn_cont_80', 'dnn_incl_50', 'dnn_incl_80', 'w_50', 'w_80']
    samples = list(samples_DXAOD.keys())
    samples, dsid_run = sys.argv[1:]
    samples = [samples]
    global FORMULAS
    FORMULAS = load_formulas()
    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_SEP_v3/'

    weights = {}
    histos  = {}
    variables = var_main
    for samp in samples:
        filt = ['dijet']
        _files, _fail, _broken = load_files(samp, folder, vnames=list(variables.keys()), filt=filt)
        histos[samp] = {}
        dsids = list(_files.keys())
        for dsid in dsids:
            if not dsid == dsid_run: continue
            files = _files[dsid]
            histos[samp][dsid] = {}
            for vname, var in variables.items():
                if not '2D' in vname:
                    var=[var]
                histos[samp][dsid][vname] = {}
                for tag in TAGGERS+['all']:
                    histos[samp][dsid][vname][tag] = dh.Histogram(*var, storage=dh.storage.Double())
                    #histos[samp][dsid][vname][tag] = Hist(var, storage=hist.storage.Double())
            print('Initialised', samp, dsid)
            photon = False if not 'gammajet' in filt else True
            histos[samp][dsid] = fill_histos(files, histos[samp][dsid], list(variables.keys()), FORMULAS, photon)
            print('Saving sample histograms')
            with open('pkl/dask_SEP_v1_'+samp+'_'+dsid+'.pkl', 'wb') as file:
                pkl.dump(histos[samp][dsid], file, protocol=pkl.HIGHEST_PROTOCOL)
            del files
            del _files[dsid]
            del histos[samp][dsid]

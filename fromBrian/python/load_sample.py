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
from grid.samples_ufo_newvars import samples_DXAOD
from functools import reduce
from termcolor import colored, cprint
from itertools import repeat
import multiprocessing as mp

def add_hists(a, b):
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

def clean(List):
    return list(filter(bool,List))

def get_weight(sample, dsid):
    xsec_file = 'sample_xsections_newvars.txt'
    xsec_file = pd.read_csv(xsec_file, names=['dsid', 'filt', 'xsec', 'shower'], header=None, delimiter=' ')

    nevt_file = 'data/weights_dijet.root'
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
    files_out = []
    for root, dir, files in os.walk(folder):
        for file in files:
            if all(map(lambda x: x in file, kws)):
                files_out.append(file)
    return files_out

def load_formulas():
    path = '/cvmfs/atlas.cern.ch/repo/sw/database/GroupData/BoostedJetTaggers/JSSWTopTaggerDNN/Rel21/UFO_tests/'
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

def get_sample(sample, folder, ax1, ax2, filt=[], debug=False):
    fnames = samples_DXAOD[sample]
    cprint(sample, 'blue')
    hists = {}
    fail = []
    taggers = ['dnn_cont_50', 'dnn_cont_80', 'dnn_incl_50', 'dnn_incl_80']
    for fname in fnames:
        dsid = fname.split('.')[1]
        tags = fname.split('.')[-1]
        new_name = find_file([dsid, tags, 'dijet']+filt, folder=folder)
        if not new_name:
            cprint(fname, 'magenta', attrs = ['bold'])
            fail.append(fname)
            continue
        hists[dsid]       , broken = get_histos(new_name, folder, ax1=ax1, ax2=ax2           )
        hists[dsid]['all'], broken = get_histos(new_name, folder, ax1=ax1, ax2=ax2, cut='all')
        if broken:
            cprint(fname, 'red', attrs = ['blink'])
            for b in broken:
                fail.append(folder+b[0])
                cprint('\tFailed '+b[0], 'red', attrs=['bold'])
                print('\t', type(b[1]), b[1])
            continue
        else:
            cprint(fname, 'green')

        if not 'data' in sample:
            weight  = get_weight(sample, int(dsid))
            for key in taggers+['all']:
                hists[dsid][key] *= weight
    return hists, fail

def log_result(self, result):
    print("Succesfully get callback! With result: ", result)

def get_samples(folder, ax1, ax2, filt=[], debug=False, parallel=True):
    '''
    Create dictionary of histograms, summing up the individual dsids
    '''
    hists = {}
    fail = []
    taggers = ['dnn_cont_50', 'dnn_cont_80', 'dnn_incl_50', 'dnn_incl_80']
    print("Loading")
    samples = sorted(samples_DXAOD.keys())
    samples = list(filter(lambda x: not 'gamma' in x or 'data' in x, samples))
    #samples = list(filter(lambda x: 'herwig' in x, samples))
    if parallel:
        with mp.Pool(mp.cpu_count()) as pool:
            res = pool.starmap_async(get_sample, zip(samples, repeat(folder), repeat(ax1), repeat(ax2), repeat(filt), repeat(debug)))
            pool.close()
            pool.join()
        results = [x for x in res.get()]
        for i, x in enumerate(results):
            hists[samples[i]] = x[0]
            fail += x[1]
    else:
        for sample in samples:
            hists[sample], fail_s = get_sample(sample, folder, ax1=ax1, ax2=ax2, filt=filt, debug=debug)
            fail += fail_s

    for sample in samples:
        fnames = samples_DXAOD[sample]
        dsids = list(hists[sample].keys())
        for tag in taggers+['all']:
            hists_dsid = map(lambda x: hists[sample][x][tag], dsids)
            hists_dsid = clean(hists_dsid)
            try:
                hists[sample][tag] = reduce(add_hists, hists_dsid)
            except:
                hists[sample][tag] = False
        for dsid in dsids:
            del hists[sample][dsid]
    return hists, fail

def get_histos(fnames, folder, ax1=False, ax2=False, cut='pass', debug=False):
    hist_out = False
    hists, errs = {}, {}
    broken = False
    for fname in fnames:
        try:
            file = pd.read_pickle(folder+fname)
        except Exception as e:
            if broken:
                broken += [(fname, e)]
            else:
                broken = [(fname, e)]
            continue
        formulas = load_formulas()

        # Flatten
        tree = file.droplevel(1)
        tree = tree[tree['rljet_m_comb[:,0]']>50000.]

        # Decorate
        target = np.log(tree['rljet_m_comb[:,0]']/tree['rljet_pt_comb'])

        if cut == 'all':
            # Calculate weight
            if 'period' in fname:
                weight = np.ones_like(tree['rljet_m_comb[:,0]'])
            else:
                weight = (tree['weight_mc']*tree['weight_pileup'])
            # Apply cuts
            log_m_pt = target
            pt = tree['rljet_pt_comb'] / 1000.
            weight = weight
            h = Hist(ax1, ax2, storage=hist.storage.Weight())
            h.fill(y=log_m_pt, x=pt, weight=weight)
            if hist_out:
                hist_out += h
            else:
                hist_out  = h

        for name, f in formulas.items():
            # Calculate weight
            if 'period' in fname:
                weight = np.ones_like(tree['rljet_m_comb[:,0]'])
            else:
                weight = (tree['weight_mc']*tree['weight_pileup'])

            if cut=='pass':
                # Caclulate pass/fail
                if 'cont' in name:
                    tagger = tree['rljet_topTag_DNN20_TausRatio_qqb_score']
                else:
                    tagger = tree['rljet_topTag_DNN20_TausRatio_inclusive_score']
                score_cut = f
                score_cut = score_cut(tree['rljet_pt_comb']/1000.)

                # Apply cuts
                log_m_pt = target[tagger > score_cut]
                pt = tree['rljet_pt_comb'][tagger > score_cut] / 1000.
                weight = weight[tagger > score_cut]

            # Create histos
            h = Hist(ax1, ax2, storage=hist.storage.Weight())
            h.fill(y=log_m_pt, x=pt, weight=weight)
            if name in hists.keys():
                hists[name] += h
            else:
                hists[name]  = h

    if cut == 'all':
        return hist_out, broken
    else:
        return hists, broken

if __name__ == "__main__":
    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_JUN/'
    get_samples(folder, sys.argv[1:], hist.axis.Variable([450,2500], name='x'), hist.axis.Variable([-4.,0.], name='y'), debug=True)

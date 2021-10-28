import os, sys
import hist
import pickle as pkl
from python.utils.weights import get_weight
from grid.samples_ufo_newvars import samples_DXAOD
from hist.intervals import ratio_uncertainty
import mplhep as hep
import matplotlib.pyplot as plt
from termcolor import colored, cprint
from functools import reduce
import numpy as np
import argparse
from matplotlib.ticker import LogLocator, NullFormatter
import multiprocessing as mp
from python.configs.vars import var_main

def plot_1d(vname, tag, main, mc, alt=False, **kwargs):
    errps = {'hatch':'////', 'facecolor':'none', 'lw': 0, 'color': 'k', 'alpha': 0.4}
    hep.style.use(hep.style.ATLAS)
    f, axs = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw=dict(height_ratios=[3, 1], hspace=0.1), sharex=True)
    # Histo management
    mc_label, mc_col, mc = zip(*mc)
    bkg = reduce(lambda x,y: x+y, mc)
    main_label, main_col, main = main
    if alt:
        alt_label, alt_col, alt = zip(*alt)
        labels = list(alt_label)+[main_label]
        signals = list(alt)+[main]
        colours = list(alt_col)+[main_col]
    else:
        signals = [main]
        labels = [main_label]
        colours = [main_col]
    ratios  = [(data+((-1.)*bkg)).sum()/x.sum() for x in signals]
    signals = [bkg+(r*x) for r, x in zip(ratios, signals)]
    labels  = [label+'\n[x%.2f]'%r for label, r in zip(labels, ratios)]

    # Upper plot
    # Data (errorbar)
    hep.histplot(data, label='Data', c='black',
                 histtype='errorbar', xerr=True, ax=axs[0])
    # Bkgd (filled)
    hep.histplot(list(mc), histtype='fill', stack=True, ax=axs[0],
                 label = list(mc_label),
                 color = list(mc_col))
    ## MC error (hashed)
    axs[0].stairs(
        values=signals[-1].values() + np.sqrt(signals[-1].values()),
        baseline=signals[-1].values() - np.sqrt(signals[-1].values()),
        edges=signals[-1].axes[0].edges, label='Stat. unc.', **errps)
    ## Signal (step)
    hep.histplot(signals, histtype='step', ax=axs[0],
                 label = labels,
                 color = colours,
                 )

    # Lower plot
    # Data/MC (errorbar)
    yerr = ratio_uncertainty(data.values(), main.values(), 'poisson')
    hep.histplot([data.values()/x.values() for x in signals],
                 color = colours, bins=main.axes[0].edges,
                 ax=axs[1], histtype='step')
    # Ratio error (hashed)
    axs[1].stairs(1+yerr[1], edges=main.axes[0].edges, baseline=1-yerr[0], **errps)
    y_scale = axs[0].get_ylim()
    y_max   = np.exp(np.log(y_scale[1])*1.3)

    # Fix titles and axes
    # Upper plot
    axs[0].set_ylim([10, y_max])
    axs[0].set_ylabel('Events')
    axs[0].set_xlabel(' ')
    axs[0].set_yscale('log')
    axs[0].yaxis.set_major_locator(LogLocator(base=10, numticks=5))
    axs[0].yaxis.set_minor_locator(LogLocator(base=10, subs = np.arange(1.0, 10.0) * 0.1, numticks=10))
    # Lower plot
    axs[1].set_ylim([0.5,1.5])
    axs[1].set_ylabel('Data/MC')
    axs[1].set_xlabel(var_main[vname].label, labelpad=20)
    # Legend/Label elements
    axs[0].legend(loc='upper right', ncol=2, fontsize='small')
    hep.atlas.label(ax=axs[0], data=True, lumi=139, label='Internal')
    plt.savefig(sys.argv[1]+'/'+vname+'_'+tag+'.png')
    del f, axs

def add_dicts(a, b):
    hists = {}
    for k, v in a.items():
        hists[k] = {}
        for j, w in v.items():
            if a[k][j] and b[k][j]:
                hists[k][j] = a[k][j] + b[k][j]
            elif a[k][j]:
                hists[k][j] = a[k][j]
            elif b[k][j]:
                hists[k][j] = b[k][j]
            else:
                hists[k][j] = False

    return hists

def apply_weights(sample, dsid, hists):
    global weights
    if 'data' in sample:
        return hists
    for k, v in hists.items():
        for j, w in v.items():
            hists[k][j] = w*weights[sample][dsid]
    return hists

def sum_dsids(samp):
    global histos
    histos[samp] = []
    prefix = 'dask_SEP_v1_'
    print('Loading', samp)
    print('\t'+prefix+samp+'.pkl')
    if os.path.exists('pkl/'+prefix+'_dijet/'+prefix+samp+'.pkl'):
        with open('pkl/'+prefix+'_dijet/'+prefix+samp+'.pkl', 'rb') as f:
            histos[samp] = pkl.load(f)
    else:
        print('Running DSIDS')
        for f in samples_DXAOD[samp]:
            dsid = f.split('.')[1]
            if os.path.exists('pkl/'+prefix+'dijet/'+prefix+samp+'_'+dsid+'.pkl'):
                print('\t', 'pkl/'+prefix+'dijet/'+prefix+samp+'_'+dsid+'.pkl')
                with open('pkl/'+prefix+'dijet/'+prefix+samp+'_'+dsid+'.pkl', 'rb') as f:
                    histos[samp].append(apply_weights(samp, dsid, pkl.load(f)))

        histos[samp] = reduce(add_dicts, histos[samp])
        print('Dumping', 'pkl/'+prefix+'dijet/'+prefix+samp+'.pkl')
        with open('pkl/'+prefix+'dijet/'+prefix+samp+'.pkl', 'wb') as file:
            pkl.dump(histos[samp], file, protocol=pkl.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    # Load in samples
    if 'gamma' in sys.argv[1]:
        samples = [x for x in samples_DXAOD.keys() if 'gamma' in x or 'data' in x]
    else:
        samples = [x for x in samples_DXAOD.keys() if not 'gamma' in x]
    global histos
    global weights
    histos = {}
    weights = {}
    for samp in samples:
        if 'data' in samp: continue
        weights[samp] = {}
        for f in samples_DXAOD[samp]:
            dsid = f.split('.')[1]
            if 'gamma' in sys.argv[1]:
                weights[samp][dsid] = get_weight(samp, dsid, xsec_file='sample_xsections_gammajet.txt', nevt_file='data/weights_gamma.root')
            else:
                weights[samp][dsid] = get_weight(samp, dsid)

    for samp in samples:
        sum_dsids(samp)

    variables = var_main

    TAGGERS = ['dnn_cont_50', 'dnn_cont_80', 'dnn_incl_50', 'dnn_incl_80', 'w_50', 'w_80']
    for vname, var in variables.items():
        print('Plotting', vname)
        for tag in TAGGERS+['all']:
            print('\t', tag)
            data   = histos['data_2018'][vname][tag]# + \
                     #histos['data_2016'][vname][tag]# + \
                     #histos['data_2017'][vname][tag] + \
                     #histos['data_2018'][vname][tag]

            if 'gamma' in sys.argv[1]:
                wzg = histos['wz_gamma_mc16a'][vname][tag] + \
                      histos['wz_gamma_mc16d'][vname][tag] + \
                      histos['wz_gamma_mc16e'][vname][tag]

                ttg = histos['ttbar_gamma_mc16a'][vname][tag] + \
                      histos['ttbar_gamma_mc16d'][vname][tag] + \
                      histos['ttbar_gamma_mc16e'][vname][tag]

                sherpa = histos['sherpa_gammajet_mc16a'][vname][tag] + \
                         histos['sherpa_gammajet_mc16d'][vname][tag] + \
                         histos['sherpa_gammajet_mc16e'][vname][tag]

            else:
                wjets  = histos['sherpa_wjets_mc16e'][vname][tag]# + \
                         #histos['sherpa_wjets_mc16d'][vname][tag] + \
                         #histos['sherpa_wjets_mc16e'][vname][tag]

                zjets  = histos['sherpa_zjets_mc16e'][vname][tag]# + \
                         #histos['sherpa_zjets_mc16d'][vname][tag] + \
                         #histos['sherpa_zjets_mc16e'][vname][tag]

                ttbar  = histos['ttbar_allhad_mc16e'][vname][tag]# + \
                         #histos['ttbar_allhad_mc16d'][vname][tag] + \
                         #histos['ttbar_allhad_mc16e'][vname][tag]

                pythia = histos['pythia_dijet_mc16e'][vname][tag]# + \
                         #histos['pythia_dijet_mc16d'][vname][tag] + \
                         #histos['pythia_dijet_mc16e'][vname][tag]

                sherpa = histos['sherpa_alt_dijet_mc16e'][vname][tag]# + \
                         #histos['sherpa_alt_dijet_mc16d'][vname][tag] + \
                         #histos['sherpa_alt_dijet_mc16e'][vname][tag]

                lund   = histos['sherpa_lund_dijet_mc16e'][vname][tag]# + \
                         #histos['sherpa_lund_dijet_mc16d'][vname][tag] + \
                         #histos['sherpa_lund_dijet_mc16e'][vname][tag]

                dipole = histos['herwig_dipole_dijet_mc16e'][vname][tag]# + \
                         #histos['herwig_dipole_dijet_mc16d'][vname][tag] + \
                         #histos['herwig_dipole_dijet_mc16e'][vname][tag]

                ang    = histos['herwig_angular_dijet_mc16e'][vname][tag]# + \
                         #histos['herwig_angular_dijet_mc16d'][vname][tag] + \
                         #histos['herwig_angular_dijet_mc16e'][vname][tag]

            if 'gamma' in sys.argv[1]:
                plot_1d(vname, tag, data=data,
                                    main=('$\gamma$+jet (Sherpa)', 'tab:green', sherpa),
                                    mc=[
                                       ('$t\overline{t}+\gamma$', 'tab:purple', ttg),
                                       ('$V$+gamma', 'tab:brown', wzg),
                                       ],
                        )
            else:
                plot_1d(vname, tag, data=data,
                                    main=('Dijet (Pythia)', 'tab:green', pythia),
                                    mc=[
                                        ('$t\overline{t}$', 'tab:purple', ttbar),
                                        ('$W$+jets', 'tab:olive', wjets),
                                        ('$Z$+jets', 'tab:brown', zjets),
                                        ],
                                    alt=[
                                        ('Herwig (Dipole)',  'tab:blue',   dipole),
                                        ('Herwig (Angular)', 'tab:cyan',   ang),
                                        ('Sherpa',           'tab:red',    lund),
                                        ('Sherpa (Lund)',    'tab:orange', sherpa)
                                    ],
                        )


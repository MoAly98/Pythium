import os, sys, hist
from python.load_sample import get_samples, get_histos
import pandas as pd
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from matplotlib import colors
import pickle as pkl
from hist import Hist
from termcolor import colored, cprint

import matplotlib.transforms as transforms
rot = transforms.Affine2D().rotate_deg(90).scale(-1, 1)

def divide(a, b, out):
    out[0][...] = np.divide(a[0].to_numpy(), b[0].to_numpy())[0]
    out[1][...] = ((a[1].values()**2)/(a[0].values()) + (b[1].values()**2)/(b[0].values()))*(out[0].values()**2)
    return out

def pctg_err(vals, vrnc, out):
    out[...] = np.sqrt(vrnc)/vals
    return

def get_med_mad(h):
    from scipy.stats import median_abs_deviation as mad
    width = mad(np.ravel(h.values()), nan_policy='omit')
    med   = np.nanmedian(np.ravel(h.values()))
    return med, width

def plot_all(num, den, sf, name, labels=['',''], log=None, cmax=False):
    hep.style.use(hep.style.ATLAS)
    f, axs = plt.subplots(3,2, figsize=(8, 12), sharex=True, sharey=True)
    sf = divide(num, den, sf)
    pctg_err(sf[0], sf[1], sf[1])
    pctg_err(num[0], num[1], num[1])
    pctg_err(den[0], den[1], den[1])
    # Top left (SF)
    med, width = get_med_mad(sf[0])
    hep.hist2dplot(sf[0], ax=axs[0][0], cmin=0.01, cmax=med+5.*width)
    # Top right (SF err)
    med, width = get_med_mad(sf[1])
    hep.hist2dplot(sf[1], ax=axs[0][1], cmin=0., cmax=med+5.*width)
    # Middle left (signal)
    if cmax:
        med, width = get_med_mad(num[0])
        hep.hist2dplot(num[0], ax=axs[1][0] , cmin=0.01, norm=log, cmax=med+5.*width)
    else:
        hep.hist2dplot(num[0], ax=axs[1][0] , cmin=0.01, norm=log)
    # Middle left (signal error)
    med, width = get_med_mad(num[1])
    hep.hist2dplot(num[1], ax=axs[1][1] , cmin=0., cmax=med+5.*width)
    # Bottom right (data-bkgd)
    if cmax:
        med, width = get_med_mad(den[0])
        hep.hist2dplot(den[0], ax=axs[2][0] , cmin=0.01, norm=log, cmax=med+5.*width)
    else:
        hep.hist2dplot(den[0], ax=axs[2][0] , cmin=0.01, norm=log)
    # Bottom left (data-bkgd error)
    med, width = get_med_mad(den[1])
    hep.hist2dplot(den[1], ax=axs[2][1] , cmin=0., cmax=med+5.*width)
    # Labels (top left)
    for i in [0, 1, 2]:
        for j in [0,1]:
            axs[i][j].set_xlabel('')
            axs[i][j].set_ylabel('')
    axs[0][0].set_title('SF',                                          fontsize=15)
    axs[0][1].set_title('$\sigma_{SF}$',                               fontsize=15)
    axs[1][0].set_title('{num}'                .format(num=labels[0]), fontsize=15)
    axs[1][1].set_title('$\sigma$({num})/{num}'.format(num=labels[0]), fontsize=15)
    axs[2][0].set_title('{den}'                .format(den=labels[1]), fontsize=15)
    axs[2][1].set_title('$\sigma$({den})/{den}'.format(den=labels[1]), fontsize=15)
    f.text(0.5,0.05, '$p_{T}[GeV]$'  , ha='center', va='center', fontsize=20)
    f.text(0.05,0.5, '$log(m/p_{T})$', ha='center', va='center', fontsize=20, rotation=90)
    plt.savefig(sys.argv[2]+'/'+name+'.png')

def plot_project(h, name):
    hep.style.use(hep.style.ATLAS)
    # start with a square Figure
    fig = plt.figure(figsize=(8, 8))

    # Add a gridspec with two rows and two columns and a ratio of 2 to 7 between
    # the size of the marginal axes and the main axes in both directions.
    # Also adjust the subplot parameters for a square plot.
    gs = fig.add_gridspec(2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),
                        left=0.1, right=0.9, bottom=0.1, top=0.9,
                        wspace=0.05, hspace=0.05)

    ax = fig.add_subplot(gs[1, 0])
    ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)
    ax_histx.set_yscale('log')
    ax_histy.set_xscale('log')
    ax_histx.set_ylim([1., 1e7])
    ax_histy.set_xlim([1., 1e7])
    plt.tight_layout()

    hep.hist2dplot(h, ax=ax, cbar=False, norm=colors.LogNorm())
    hep.histplot(h.project('x'), ax=ax_histx)
    hep.histplot(h.project('y'), ax=ax_histy, transform=rot+ax_histy.transData)
    hep.atlas.label(data=True, lumi=139, loc=0, ax=ax_histx)
    hep.atlas.text('Internal', loc=0, ax=ax_histx)
    ax_histx.set_ylabel('Events')
    ax_histy.set_xlabel('Events')
    ax_histx.set_xlabel('')
    plt.setp(ax_histx.get_xticklabels(), visible=False)
    plt.setp(ax_histy.get_yticklabels(), visible=False)
    plt.savefig(sys.argv[2]+'/'+name+'.png', bbox_inches = "tight")

def projections(num, den, name, title):
    hep.style.use(hep.style.ATLAS)
    n_plts = sf[0].axes['x'].size
    f, axs = plt.subplots(n_plts,1, figsize=(4,4*n_plts), sharex=True)
    plt.tight_layout()
    edges = num[0].axes['y'].edges
    for i in range(n_plts):
        hep.histplot([num[0][:,i], den[0][:,i]], ax=axs[i], label=[title, 'Data-bkgd'])
        if i < n_plts - 1:
            axs[i].set_xlabel('')
        axs[i].set_ylabel('Events')
        axs[i].legend()
        axs[i].set_ylim([0.,None])
        hep.atlas.label('Internal', data=True, lumi=139.,
                        rlabel='$log(m/p_{{T}})$=[{lo}, {hi}]'.format(lo=edges[i], hi=edges[i+1]),
                        ax=axs[i], loc=3)
    plt.savefig(sys.argv[2]+'/'+'proj_logmpt_'+name+'.png', bbox_inches = "tight")


def make_hist(ax1, ax2):
    return Hist(ax1, ax2, storage=hist.storage.Double())

if __name__ == "__main__":
    folder = '/eos/atlas/user/b/brle/slimmed_SEP/'
    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_SEP/'

    ax1 = hist.axis.Variable([ 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300, 1400, 1500, 1700, 2500, ], name='x', label=r'$p_{T}$[GeV]'  )
    ax2 = hist.axis.Variable([ -4., -2., -1.6, -1.4, -1.2, -1., -0.8, -0.7, -0.6, -0.55, -0.5, 0. ], name='y', label=r'$log(m/p_{T})$')

    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'rb') as file:
            hists = pkl.load(file)
    else:
        hists, fail = get_samples(folder, ax1, ax2)
        with open(sys.argv[1], 'wb') as file:
            pkl.dump(hists, file, protocol=pkl.HIGHEST_PROTOCOL)

        print('#################################')
        cprint("Failed", 'red', attrs=['bold'])
        for f in fail:
            print(f)
        print('#################################')

    data   = hists['data_2015']['all'] + \
             hists['data_2016']['all'] + \
             hists['data_2017']['all'] + \
             hists['data_2018']['all']

    bkgd   = hists['sherpa_wjets_mc16a']['all'] + \
             hists['sherpa_wjets_mc16d']['all'] + \
             hists['sherpa_wjets_mc16e']['all'] + \
             hists['sherpa_zjets_mc16a']['all'] + \
             hists['sherpa_zjets_mc16d']['all'] + \
             hists['sherpa_zjets_mc16e']['all'] + \
             hists['ttbar_allhad_mc16a']['all'] + \
             hists['ttbar_allhad_mc16d']['all'] + \
             hists['ttbar_allhad_mc16e']['all']

    pythia_all = hists['pythia_dijet_mc16a']['all'] + \
                 hists['pythia_dijet_mc16d']['all'] + \
                 hists['pythia_dijet_mc16e']['all']

    sherpa_all = hists['sherpa_alt_dijet_mc16a']['all'] + \
                 hists['sherpa_alt_dijet_mc16d']['all'] + \
                 hists['sherpa_alt_dijet_mc16e']['all']

    lund_all   = hists['sherpa_lund_dijet_mc16a']['all'] + \
                 hists['sherpa_lund_dijet_mc16d']['all'] + \
                 hists['sherpa_lund_dijet_mc16e']['all']

    dipole_all = hists['herwig_dipole_dijet_mc16a']['all'] + \
                 hists['herwig_dipole_dijet_mc16d']['all'] + \
                 hists['herwig_dipole_dijet_mc16e']['all']

    ang_all    = hists['herwig_angular_dijet_mc16a']['all'] + \
                 hists['herwig_angular_dijet_mc16d']['all'] + \
                 hists['herwig_angular_dijet_mc16e']['all']

    data_sub_all = (data+(1.*bkgd))
    del data, bkgd

    for tag in hists['data_2015'].keys():
        if tag is 'all': continue
        print('Plotting', tag)
        data   = hists['data_2015'][tag] + \
                 hists['data_2016'][tag] + \
                 hists['data_2017'][tag] + \
                 hists['data_2018'][tag]

        bkgd   = hists['sherpa_wjets_mc16a'][tag] + \
                 hists['sherpa_wjets_mc16d'][tag] + \
                 hists['sherpa_wjets_mc16e'][tag] + \
                 hists['sherpa_zjets_mc16a'][tag] + \
                 hists['sherpa_zjets_mc16d'][tag] + \
                 hists['sherpa_zjets_mc16e'][tag] + \
                 hists['ttbar_allhad_mc16a'][tag] + \
                 hists['ttbar_allhad_mc16d'][tag] + \
                 hists['ttbar_allhad_mc16e'][tag]

        pythia = hists['pythia_dijet_mc16a'][tag] + \
                 hists['pythia_dijet_mc16d'][tag] + \
                 hists['pythia_dijet_mc16e'][tag]

        sherpa = hists['sherpa_alt_dijet_mc16a'][tag] + \
                 hists['sherpa_alt_dijet_mc16d'][tag] + \
                 hists['sherpa_alt_dijet_mc16e'][tag]

        lund   = hists['sherpa_lund_dijet_mc16a'][tag] + \
                 hists['sherpa_lund_dijet_mc16d'][tag] + \
                 hists['sherpa_lund_dijet_mc16e'][tag]

        dipole = hists['herwig_dipole_dijet_mc16a'][tag] + \
                 hists['herwig_dipole_dijet_mc16d'][tag] + \
                 hists['herwig_dipole_dijet_mc16e'][tag]

        ang    = hists['herwig_angular_dijet_mc16a'][tag] + \
                 hists['herwig_angular_dijet_mc16d'][tag] + \
                 hists['herwig_angular_dijet_mc16e'][tag]

        plot_project((data+(-1.*bkgd)), 'data_bkgsub_'+tag)
        for signal, signal_all, name, title in zip([pythia, sherpa, lund, dipole, ang],
                                                   [pythia_all, sherpa_all, lund, dipole_all, ang_all],
                                                   ['pythia', 'sherpa', 'sherpa_lund', 'herwig_dipole', 'herwig_angular'],
                                                   ['Pythia', 'Sherpa', 'Sherpa (Lund)', 'Herwig (Dipole)', 'Herwig (Angular)']):
            print("\t", name)
            # Initiate hists
            sig     = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            dat     = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            sig_all = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            dat_all = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            sig_eff = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            sig_rej = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            dat_eff = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            dat_rej = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            sf_eff  = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            sf_rej  = (make_hist(ax1, ax2), make_hist(ax1, ax2))
            sf      = (make_hist(ax1, ax2), make_hist(ax1, ax2))

            # Get components
            sig[0][...], sig[1][...] = signal.values(), signal.variances()
            dat[0][...], dat[1][...] = (data+(bkgd*-1.)).values(), (data+(bkgd*-1.)).variances()

            sig_all[0][...], sig_all[1][...] = signal_all.values(), signal_all.variances()
            dat_all[0][...], dat_all[1][...] = data_sub_all.values(), data_sub_all.variances()

            # Fill
            sig_eff = divide(sig, sig_all, sig_eff)
            dat_eff = divide(dat, dat_all, dat_eff)

            sig_rej = divide(sig_all, sig, sig_rej)
            dat_rej = divide(dat_all, dat, dat_rej)

            # Make plots
            projections(sig, dat, name+'_'+tag, title)
            plot_project(signal, 'project_'+name+'_'+tag)
            plot_all(sig, dat, sf, 'yld_'+name+'_'+tag, \
                     labels=[name, '(Data-Bkgd)'], log=colors.LogNorm())
            plot_all(sig_eff, dat_eff, sf_eff, 'eff_'+name+'_'+tag, \
                     labels=['$\epsilon$({})'.format(name), '$\epsilon$(Data-Bkgd)'], cmax=True)
            plot_all(sig_rej, dat_rej, sf_rej, 'rej_'+name+'_'+tag, \
                     labels=['Rej({})'.format(name), 'Rej(Data-Bkgd)'], cmax=True)


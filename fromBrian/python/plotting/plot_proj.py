import os, sys, hist
import pickle as pkl
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from termcolor import colored, cprint

# Sample loader  and organiser
from python.load_sample import get_samples, get_histos
from python.utils.hists import HistoDF
from python.configs.dicts import samples_dict

# hist imports
from hist import Hist
from hist.intervals import ratio_uncertainty

# Matplotlib imports
import matplotlib.transforms as transforms
from matplotlib import colors
from matplotlib.ticker import LogLocator, NullFormatter
rot = transforms.Affine2D().rotate_deg(90).scale(-1, 1)
hep.style.use(hep.style.ATLAS)

def plot_project(h, name):
    # Set up axes
    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),
                        left=0.1, right=0.9, bottom=0.1, top=0.9,
                        wspace=0.05, hspace=0.05)

    ax = fig.add_subplot(gs[1, 0])
    ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)
    ax_histx.set_yscale('log')
    ax_histy.set_xscale('log')
    plt.tight_layout()

    # Draw plots
    hep.hist2dplot(h, ax=ax, cbar=False, norm=colors.LogNorm())
    hep.histplot(h.project('x'), ax=ax_histx)
    hep.histplot(h.project('y'), ax=ax_histy, transform=rot+ax_histy.transData)

    # Fix labelling and save
    hep.atlas.label(data=True, lumi=139, loc=0, ax=ax_histx)
    hep.atlas.text('Internal', loc=0, ax=ax_histx)
    ax_histx.set_ylabel('Events')
    ax_histy.set_xlabel('Events')
    ax_histx.set_xlabel('')
    plt.setp(ax_histx.get_xticklabels(), visible=False)
    plt.setp(ax_histy.get_yticklabels(), visible=False)
    plt.savefig(sys.argv[2]+'/'+name+'.png', bbox_inches = "tight")

def plot_2d_stack_data_mc(signal, data, name, **kwargs):
    hep.style.use(hep.style.ATLAS)
    # start with a square Figure
    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(2, 3,  width_ratios=(7, 2, 0.5), height_ratios=(2, 7),
                        left=0.1, right=0.9, bottom=0.1, top=0.9,
                        wspace=0.05, hspace=0.05)

    # Format axes
    ax = fig.add_subplot(gs[1, 0])
    ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)
    ax_colz  = fig.add_subplot(gs[1, 2])
    ax_histx.set_yscale('log')
    ax_histy.set_xscale('log')
    ax_histx.yaxis.set_major_locator(LogLocator(base=10, numticks=5))
    ax_histx.yaxis.set_minor_locator(LogLocator(base=10, subs = np.arange(1.0, 10.0) * 0.1, numticks=10))
    ax_histy.xaxis.set_major_locator(LogLocator(base=10, numticks=5))
    ax_histy.xaxis.set_minor_locator(LogLocator(base=10, subs = np.arange(1.0, 10.0) * 0.1, numticks=10))
    ax_histy.xaxis.set_minor_formatter(NullFormatter())
    ax_histx.yaxis.set_minor_formatter(NullFormatter())
    plt.tight_layout()

    # Calculate data/mc
    mc = signal
    x = [signal.project('x')]
    y = [signal.project('y')]
    for k in kwargs.keys():
        mc += kwargs[k]
        x.append(kwargs[k].project('x'))
        y.append(kwargs[k].project('y'))
    ratio = data.values() / mc.values()

    # Draw plots
    hep.hist2dplot(ratio, xbins=ax1, ybins=ax2, ax=ax, cbarax=ax_colz, vmin=0.5, vmax=1.5, cbarlabel='Data/MC')
    hep.histplot(data.project('x'), ax=ax_histx,
                 histtype='errorbar', color='black',
                 markersize=5, xerr=True, yerr=True,
                 label='Data')
    ax_histx.stairs(
              values=mc.project('x').values()+np.sqrt(mc.project('x').variances()),
              baseline=mc.project('x').values()-np.sqrt(mc.project('x').variances()),
              edges=mc.axes[0].edges, hatch='////', facecolor='none',
              lw=0, color='k', alpha=0.4, label='Stat Unc.'
              )
    hep.histplot(x, label=[title]+list(kwargs.keys()), ax=ax_histx, histtype='fill')

    hep.histplot(data.project('y'), ax=ax_histy,
                 histtype='errorbar', color='black',
                 markersize=5, xerr=True, yerr=True,
                 transform=rot+ax_histy.transData)
    hep.histplot(y, ax=ax_histy, histtype='fill', transform=rot+ax_histy.transData)

    # Fix labelling and save
    hep.atlas.label(data=True, lumi=139, loc=0, ax=ax_histx)
    hep.atlas.text('Internal', loc=0, ax=ax_histx)
    ax_histx.set_ylim(bottom=10)
    ax_histy.set_xlim(left=10)
    ax.set_ylabel('log(m/$p_{T}$)')
    ax.set_xlabel('$p_{T}$ [GeV]')
    ax_histx.set_ylabel('Events')
    ax_histy.set_xlabel('Events')
    ax_histx.set_xlabel('')
    handles, labels = ax_histx.get_legend_handles_labels()
    handles = [handles[-1]] + handles[1:-1] + [handles[0]]
    labels  = [labels [-1]] + labels [1:-1] + [labels [0]]
    ax_histx.legend(handles, labels, loc='lower left',
                    borderaxespad=0, bbox_to_anchor=(1.0,0.))
    plt.setp(ax_histx.get_xticklabels(), visible=False)
    plt.setp(ax_histy.get_yticklabels(), visible=False)
    plt.setp(ax.get_xticklabels(), rotation=15, ha='right')
    plt.savefig(sys.argv[2]+'/'+name+'.png', bbox_inches = "tight")

def plot_proj_stack_data_mc(signal, data, name, **kwargs):
    '''
    Plot slices of log(m/pT)
    '''
    hep.style.use(hep.style.ATLAS)
    n_plts = signal.axes['y'].size
    f, axs = plt.subplots(2, n_plts, figsize=(4*n_plts,6),
                          gridspec_kw=dict(height_ratios=[4,1]), sharex=True)
    plt.tight_layout()
    mc  = signal
    mcs = [signal]
    for k in kwargs.keys():
        mc += kwargs[k]
        mcs.append(kwargs[k])
    edges = signal.axes['y'].edges
    for i in range(n_plts):
        n = n_plts - 1 - i
        hep.histplot(data[:,i], ax=axs[0][n], label='Data',
                     histtype='errorbar', color='black', markersize=3, xerr=True)
        hep.histplot(list(map(lambda x: x[:,i], mcs)), ax=axs[0][n],
                     label=[title]+list(map(lambda x: samples_dict[x], kwargs.keys())), histtype='fill')
        axs[0][n].stairs(
                values  =mc[:,i].values()+np.sqrt(mc[:,i].variances()),
                baseline=mc[:,i].values()-np.sqrt(mc[:,i].variances()),
                edges=mc.axes[0].edges, hatch='////', facecolor='none',
                lw=0, color='k', alpha=0.4, label='Stat Unc.'
                )
        # Ratio plot
        yerr = ratio_uncertainty(data[:,i].values(), mc[:,i].values())
        axs[1][n].stairs(1+yerr[1], baseline=1-yerr[0],
                        edges=mc[:,i].axes[0].edges, hatch='////', facecolor='none',
                        lw=0, color='k', alpha=0.4,
                        )
        hep.histplot(data[:,i].values()/mc[:,i].values(), mc[:,i].axes[0].edges,
                     yerr=np.sqrt(data[:,i].values())/mc[:,i].values(), xerr=True,
                     ax=axs[1][n], histtype='errorbar', color='k', markersize=3)

        # Fix labels
        if n < n_plts - 1:
            axs[0][n].set_xlabel('')
        axs[0][n].set_xlabel('')
        axs[1][n].set_xlabel('$p_{T}$')
        axs[0][n].set_ylabel('')
        axs[0][n].set_yscale('log')
        axs[0][n].set_ylim([0.,None])
        axs[1][n].set_ylim([0.8,1.2])
        axs[0][n].set_title('$log(m/p_{{T}})$=[{lo}, {hi}]'.format(lo=edges[i], hi=edges[i+1]))
    axs[0][n].legend(loc='upper right')
    axs[0][n].set_ylabel('Events')
    axs[1][n].set_ylabel('Data/MC')
    plt.savefig(sys.argv[2]+'/'+name+'.png', bbox_inches = "tight")


if __name__ == "__main__":
    folder = '/eos/atlas/user/b/brle/slimmed_JUN/'
    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_JUN/'

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

    samples = ['pythia_dijet', 'herwig_dipole_dijet', 'herwig_angular_dijet', 'sherpa_alt_dijet', 'sherpa_lund_dijet',
               'data', 'sherpa_wjets', 'sherpa_zjets', 'ttbar_allhad']
    tags    = ['dnn_cont_50', 'dnn_cont_80','dnn_incl_50', 'dnn_incl_80']
    # Fill HistoDF object
    hist_df = HistoDF(samples, tags)
    for tag in tags:
        data = hists['data_2015'][tag] + \
               hists['data_2016'][tag] + \
               hists['data_2017'][tag] + \
               hists['data_2018'][tag]
        hist_df.set_hist(( 'data', tag ), 'Hist', data)
        for samp in samples:
            if samp == 'data': continue
            data = hists[samp+'_mc16a'][tag] + \
                   hists[samp+'_mc16d'][tag] + \
                   hists[samp+'_mc16e'][tag]
            hist_df.set_hist( ( samp , tag ), 'Hist', data )

    for tag in tags:
        print('Plotting', tag)
        for name in ['pythia', 'sherpa_alt', 'sherpa_lund', 'herwig_dipole', 'herwig_angular']:
            signal = hist_df.get_hist( (name+'_dijet', tag), 'Hist' )
            data   = hist_df.get_hist( ('data', tag), 'Hist' )
            wjets  = hist_df.get_hist( ('sherpa_wjets', tag), 'Hist' )
            zjets  = hist_df.get_hist( ('sherpa_zjets', tag), 'Hist' )
            ttbar  = hist_df.get_hist( ('ttbar_allhad', tag), 'Hist' )
            title  = samples_dict[name]
            print('\t', title)
            #plot_project(signal, 'project_'+name+'_'+tag)
            plot_2d_stack_data_mc(signal, data,
                                  'project_ratio_2d_stack_'+name+'_'+tag,
                                  wjets = wjets,
                                  zjets = zjets,
                                  ttbar = ttbar)
            plot_proj_stack_data_mc(signal, data,
                                    'project_logmpt_ratio_stack_'+name+'_'+tag,
                                    wjets = wjets,
                                    zjets = zjets,
                                    ttbar = ttbar)

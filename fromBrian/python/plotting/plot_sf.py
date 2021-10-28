import os, sys, hist
import pickle as pkl
import numpy as np
import mplhep as hep
import pandas as pd
import matplotlib.pyplot as plt

# Sample loader  and organiser
from python.load_sample import get_samples, get_histos
from python.utils.hists import HistoDF, Histo, recip
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

def get_med_mad(h):
    from scipy.stats import median_abs_deviation as mad
    try:
        h = h.values()
    except:
        pass
    width = mad(np.ravel(h), nan_policy='omit')
    med   = np.nanmedian(np.ravel(h))
    return med, width

def set_zrange(lo=None, hi=None):
    return({'vmin': lo, 'vmax': hi})

def plot_all(num, den, name, labels=['',''], log=None, vmax=False, xbins=None, ybins=None, mode=False):
    hep.style.use(hep.style.ATLAS)
    f, axs = plt.subplots(3,2, figsize=(8, 12), sharex=True, sharey=True)

    sf = num / den
    bins={'xbins': xbins, 'ybins': ybins}
    zrange={'vmin':None, 'vmax':None}

    # Top (SF, sig(SF)/SF)
    hep.hist2dplot(sf.values,
                   ax=axs[0][0],
                   vmin=0.5, vmax=1.5,
                   **bins)
    hep.hist2dplot(sf.errors[0]/sf.values,
                   ax=axs[0][1],
                   vmin=0., vmax=1.,
                   **bins)
    # Middle (signal, sig(signal)/signal)
    if vmax:
        lo=0.1 if log else 0.
        med, width = get_med_mad(num.values)
        zrange = set_zrange(lo=lo, hi=med+5.*width)
    kwargs={**bins, **zrange}
    hep.hist2dplot(num.values, ax=axs[1][0], norm=log, **kwargs)
    hep.hist2dplot(num.errors[0]/num.values,
                   ax=axs[1][1],
                   vmin=0., vmax=1.,
                   **bins)
    # Bottom left (data-bkgd)
    if vmax:
        lo=0.1 if log else 0.
        med, width = get_med_mad(den.values)
        zrange = set_zrange(lo=lo, hi=med+5.*width)
    kwargs={**bins, **zrange}
    hep.hist2dplot(den.values, ax=axs[2][0], norm=log, **kwargs)
    hep.hist2dplot(den.errors[0]/den.values,
                   ax=axs[2][1],
                   vmin=0., vmax=1.,
                   **bins)

    # Fix labelling, add plot titles
    for i in [0, 1, 2]:
        for j in [0,1]:
            axs[i][j].set_xlabel('')
            axs[i][j].set_ylabel('')
    axs[0][0].set_title('SF',                                          fontsize=15)
    axs[0][1].set_title('$\sigma_{SF}/SF$',                            fontsize=15)
    axs[1][0].set_title('{num}'                .format(num=labels[0]), fontsize=15)
    axs[1][1].set_title('$\sigma$({num})/{num}'.format(num=labels[0]), fontsize=15)
    axs[2][0].set_title('{den}'                .format(den=labels[1]), fontsize=15)
    axs[2][1].set_title('$\sigma$({den})/{den}'.format(den=labels[1]), fontsize=15)
    f.text(0.5,0.05, '$p_{T}[GeV]$'  , ha='center', va='center', fontsize=20)
    f.text(0.05,0.5, '$log(m/p_{T})$', ha='center', va='center', fontsize=20, rotation=90)
    plt.savefig(sys.argv[2]+'/'+name+'.png')

class Proj1DPlots():
    def __init__(self, name, title, data={}, signal={}, nrows=[], ncols=False, **kwargs):
        self.name   = name
        self.title  = title
        self.data   = data
        self.signal = signal
        self.nrows  = len(data.keys()) if not nrows else len(nrows)
        self.ncols  = ncols if ncols else False
        for k, v in data.items():
            self.ncols = v.axes['y'].size
            self.edges = v.axes['x'].edges
            self.bins  = v.axes['y'].edges
            break
        self.f = False
        self.axs = False
        for k, v in kwargs.items():
            setattr(self, k, v)

    def makeAxes(self, **kwargs):
        hep.style.use(hep.style.ATLAS)
        base_ratio = [4,1]
        height_ratios = []
        for i in range(self.nrows):
            height_ratios += base_ratio
        self.f, self.axs = plt.subplots(2*self.nrows, self.ncols,
                                        figsize=(4*self.ncols ,6*self.nrows),
                                        gridspec_kw=dict(height_ratios=height_ratios),
                                        sharex=True)
        plt.tight_layout()

    def addRows(self, row, k):
        row = row*2
        dat_err = dict(xerr=True, histtype='errorbar', color = 'black', markersize=3)
        sig_err = dict(color='darkgreen', fill=True, lw=0, alpha=0.4)
        for i in range(self.ncols):
            n = self.ncols - 1 - i
            sig   =  self.signal[k].values   [:,i]
            dat   =  self.data  [k].values   [:,i]
            if k=='Events':
                sig_e = [self.signal[k].errors[:,i] for j in range(2)]
                dat_e = [self.data  [k].errors[:,i] for j in range(2)]
            else:
                sig_e = [self.signal[k].errors[j][:,i] for j in range(2)]
                dat_e = [self.data  [k].errors[j][:,i] for j in range(2)]
            # Main plot
            hep.histplot(dat, self.edges,
                         ax=self.axs[row][n], label='Data',
                         yerr=dat_e[0],
                         **dat_err)
            self.axs[row][n].stairs(
                    values   =sig+np.sqrt(sig_e[0]),
                    baseline =sig-np.sqrt(sig_e[1]),
                    edges=self.edges,
                    label=self.title,
                    **sig_err
                    )
            # Ratio plot
            hep.histplot(dat/sig, self.edges,
                        yerr=dat/sig*np.sqrt((dat_e[0]/dat)**2 + (sig_e[0]/sig)**2),
                        ax=self.axs[row+1][n], **dat_err)
            yerr = ratio_uncertainty(dat, sig)
            self.axs[row+1][n].stairs(1+yerr[1], baseline=1-yerr[0],
                                      edges=self.edges, **sig_err)

    def fixAxis(self, row, key):
        # Fix labels
        row = row*2
        for i in range(self.ncols):
            n = self.ncols - 1 - i
            if n < self.ncols - 1:
                self.axs[row][n].set_xlabel('')
            self.axs[row]  [n].set_xlabel('')
            self.axs[row]  [n].set_ylabel('')
            self.axs[row+1][n].set_xlabel('')
            self.axs[row+1][n].set_ylabel('')
            if key == 'Events':
                self.axs[row]  [n].set_yscale('log')
            self.axs[row]  [n].set_ylim([0.,None])
            self.axs[row+1][n].set_ylim([0.8,1.2])

    def addLegend(self):
        self.axs[0][0].legend(loc='upper right')

    def finalise(self, row, key):
        row = 2*row
        self.axs[row]  [0].set_ylabel(key)
        self.axs[row+1][0].set_ylabel('Data/MC')
        for i in range(self.ncols):
            if row == 2*(self.nrows - 1):
                self.axs[row+1][i].set_xlabel('$p_{T}$ [GeV]')
            elif row == 0:
                self.axs[row]  [i].set_title('$log(m/p_{{T}})$=[{lo}, {hi}]'.format(lo=self.bins[i], hi=self.bins[i+1]),
                                    fontsize=16, loc='right')

    def savePlot(self, name):
        plt.savefig(sys.argv[2]+'/'+name+'.png', bbox_inches = "tight")

    def makePlot(self):
        self.makeAxes()
        for i, k in enumerate(self.data.keys()):
            self.addRows(i, k)
            self.fixAxis(i, k)
            self.finalise(i, k)
        self.addLegend()
        self.savePlot(self.name)

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
    tags    = ['dnn_cont_50', 'dnn_cont_80','dnn_incl_50', 'dnn_incl_80', 'all']
    hist_df = HistoDF(samples, tags)

    # Add histograms
    for tag in tags:
        data = hists['data_2015'][tag] + \
               hists['data_2016'][tag] + \
               hists['data_2017'][tag] + \
               hists['data_2018'][tag]
        data = Histo(data)
        hist_df.set_hist(( 'data', tag ), 'Hist', data)
        for samp in samples:
            if samp == 'data': continue
            data = hists[samp+'_mc16a'][tag] + \
                   hists[samp+'_mc16d'][tag] + \
                   hists[samp+'_mc16e'][tag]
            hist_df.set_hist(( samp , tag ), 'Hist', Histo(data))

    # Add data-bkgd
    data_sub =      hist_df.store.xs('data') + \
               (-1.*hist_df.store.xs('sherpa_wjets')) + \
               (-1.*hist_df.store.xs('sherpa_zjets')) + \
               (-1.*hist_df.store.xs('ttbar_allhad'))
    data_sub=pd.concat({'data_sub': data_sub}, names=['Samples'])
    hist_df.store=pd.concat([hist_df.store, data_sub])

    # Calculate efficiency and rejection
    num     = hist_df.store['Hist'].copy()
    den_all = hist_df.store.xs((slice(None), 'all'))
    den_all = den_all.align(num, join='left', axis=0)[0]['Hist']

    eff = num.divide(den_all, 'poisson-ratio')

    hist_df.store['Eff'] = eff.copy()
    hist_df.store['Rej'] = eff.apply(recip)

    signals = ['pythia_dijet', 'herwig_dipole_dijet', 'herwig_angular_dijet',
               'sherpa_alt_dijet', 'sherpa_lund_dijet']

    for tag in tags:
        print('Plotting', tag)
        for s in signals:
            title = samples_dict[s.replace('_dijet', '')]
            print('\t'+title)
            plot_all(hist_df.get_hist((s         , tag), 'Hist'),
                     hist_df.get_hist(('data_sub', tag), 'Hist'),
                     '_'.join(['hist', s, tag]),
                     labels=['{}'.format(title),
                             'Data-Bkgd'],
                     vmax=True, log=colors.LogNorm(),
                     xbins=ax1,
                     ybins=ax2,
                     )
            if tag == 'all': continue
            plot_all(hist_df.get_hist((s         , tag), 'Eff'),
                     hist_df.get_hist(('data_sub', tag), 'Eff'),
                     '_'.join(['eff', s, tag]),
                     labels=['$\epsilon$({})'.format(title),
                             '$\epsilon$(Data-Bkgd)'],
                     vmax=True,
                     xbins=ax1,
                     ybins=ax2,
                     )
            plot_all(hist_df.get_hist((s         , tag), 'Rej'),
                     hist_df.get_hist(('data_sub', tag), 'Rej'),
                     '_'.join(['rej', s, tag]),
                     labels=['Rej({})'.format(title),
                             'Rej(Data-Bkgd)'],
                     vmax=True,
                     xbins=ax1,
                     ybins=ax2,
                     )
            Proj1DPlots('project_1D_'+s+'_'+tag,
                        title,
                        data={
                            'Events':     hist_df.get_hist(('data_sub', tag), 'Hist'),
                            '$\epsilon$': hist_df.get_hist(('data_sub', tag), 'Eff'),
                            'Rejection':  hist_df.get_hist(('data_sub', tag), 'Rej'),
                            },
                        signal={
                            'Events':     hist_df.get_hist((s, tag), 'Hist'),
                            '$\epsilon$': hist_df.get_hist((s, tag), 'Eff'),
                            'Rejection':  hist_df.get_hist((s, tag), 'Rej'),
                            },
                        ).makePlot()

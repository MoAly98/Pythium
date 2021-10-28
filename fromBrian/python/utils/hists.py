import sys
import pickle as pkl
import pandas as pd
import numpy as np
from copy import copy
from hist import Hist
from hist.intervals import ratio_uncertainty

class HistoDF(object):
    def __init__(self, samples, tags, **kwargs):
        length = len(samples)*len(tags)
        if kwargs.keys():
            combs = pd.MultiIndex.from_product([samples, tags, [kwargs[k] for k in kwargs.keys()]],
                                         names=['Samples', 'Tags', kwargs.keys()])
            for v in kwargs.values():
                length *= len(v)
        else:
            combs  =  pd.MultiIndex.from_product([samples, tags], names=['Samples', 'Tags'])
        data=[False for x in range(length)]
        self.store = pd.DataFrame(data, index=combs, columns=['Hist'], dtype=object)

    def get_hist(self, vals, col):
        return self.store.loc[vals, col]

    def set_hist(self, vals, col, val):
        self.store.loc[ vals, col ] = val

    def append(self, other):
        self.store = pd.merge(self.store, other, left_index=True, right_on=True)

class Histo(Hist):
    def __init__(self, hist, val=None, err=None):
        Hist.__init__(self, hist)
        self.hist = hist
        self.val = val
        self.err = err

    def __truediv__(self, other):
        val = self.values / other.values
        if isinstance(self.hist, Hist) and isinstance(other, Hist):
            err = ratio_uncertainty(self.hist.values(), other.hist.values(), 'poisson-ratio')
        else:
            err = abs(val)*np.sqrt((self.errors/self.values)**2+(other.errors/other.values)**2)
        ret = Histo(self, val, err)
        ret.hist=False
        return ret

    def divide(self, other, utype):
        val = self.values / other.values
        if isinstance(self.hist, Hist) and isinstance(other, Hist):
            err = ratio_uncertainty(self.hist.values(), other.hist.values(), utype)
        ret = Histo(self, val, err)
        ret.hist=False
        return ret

    def reciprocal(self):
        self.val  = 1./self.values
        self.err  = (self.errors)*(1./self.values)**2
        self.hist = False

    @property
    def values(self):
        if isinstance(self.hist, Hist):
            return self.hist.values()
        elif not self.val is None:
            return self.val
        else:
            return IOError('Please pass either a Hist object or specify val array')

    @property
    def errors(self):
        if isinstance(self.hist, Hist):
            return np.sqrt(self.hist.variances())
        elif not self.err is None:
            return self.err
        else:
            return IOError('Please pass either a Hist object or specify err array')

def recip(x):
    tmp = copy(x)
    val  = 1./x.values
    err  = (x.errors)*(1./x.values)**2
    tmp.val = val
    tmp.err = err
    return tmp

if __name__ == '__main__':
    samples = ['pythia_dijet', 'herwig_dipole_dijet', 'herwig_angular_dijet', 'sherpa_alt_dijet', 'sherpa_lund_dijet',
               'data', 'sherpa_wjets', 'sherpa_zjets', 'ttbar_allhad']
    tags    = ['dnn_cont_50', 'dnn_cont_80','dnn_incl_50', 'dnn_incl_80', 'all']
    hist_df = HistoDF(samples, tags)
    folder = '/eos/atlas/user/b/brle/slimmed_JUN/'
    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_JUN/'

    with open(sys.argv[1], 'rb') as file:
        hists = pkl.load(file)

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

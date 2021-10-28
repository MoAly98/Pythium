import os, sys
import hist
import pickle as pkl
from python.dask_samples import get_sample_histos, load_files, reduce_histos
#from python.samples import get_sample_histos, load_files, reduce_histos
from grid.samples_ufo_newvars import samples_DXAOD
from hist.axis import Variable, Regular
from hist.intervals import ratio_uncertainty
import mplhep as hep
import matplotlib.pyplot as plt
from termcolor import colored, cprint
from functools import reduce
import numpy as np
import argparse
from matplotlib.ticker import LogLocator, NullFormatter

def plot_1d(vname, tag, **kwargs):
    errps = {'hatch':'////', 'facecolor':'none', 'lw': 0, 'color': 'k', 'alpha': 0.4}
    hep.style.use(hep.style.ATLAS)
    f, axs = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw=dict(height_ratios=[3, 1], hspace=0), sharex=True)
    mc = [kwargs['ttbar'], kwargs['wjets'], kwargs['zjets']]
    bkg = reduce(lambda x,y: x+y, mc)
    tot = bkg + kwargs['pythia']
    hep.histplot(mc+[kwargs['pythia']], stack=True, ax=axs[0],
                 label = ['$t\overline{t}$', '$W$+jets', '$Z$+jets', 'Dijet (Pythia)'], histtype='fill',
                 color = ['purple', 'green', 'yellow', 'blue'])
    hep.histplot(data, label='Data', c='black',
                 histtype='errorbar', xerr=True, ax=axs[0])
    axs[0].stairs(
        values=tot.values() + np.sqrt(tot.values()),
        baseline=tot.values() - np.sqrt(tot.values()),
        edges=tot.axes[0].edges, **errps, label='Stat. unc.')
    yerr = ratio_uncertainty(data.values(), tot.values(), 'poisson')
    hep.histplot(data.values()/tot.values(), tot.axes[0].edges, yerr=np.sqrt(data.values())/tot.values(),
                 ax=axs[1], histtype='errorbar', color='k', label="Data", xerr=True)
    axs[1].stairs(1+yerr[1], edges=tot.axes[0].edges, baseline=1-yerr[0], **errps)
    axs[1].stairs(1+yerr[1], edges=tot.axes[0].edges, baseline=1-yerr[0], **errps)
    axs[1].set_ylim([0.5,1.5])
    y_scale = axs[0].get_ylim()
    y_max   = np.exp(np.log(y_scale[1])*1.3)
    axs[0].set_ylim([10, y_max])
    axs[0].set_ylabel('Events')
    axs[1].set_xlabel(kwargs['pythia'].axes[0].label)
    axs[0].set_yscale('log')
    axs[0].yaxis.set_major_locator(LogLocator(base=10, numticks=5))
    axs[0].yaxis.set_minor_locator(LogLocator(base=10, subs = np.arange(1.0, 10.0) * 0.1, numticks=10))
    axs[0].legend()
    hep.atlas.label(ax=axs[0], data=True, lumi=139, label='Internal')
    plt.savefig(sys.argv[1]+'/'+vname+'_'+tag+'.png')
    del f, axs


if __name__ == "__main__":
    folder = '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_SEP/'

    var_beta = {
        'rljet_pt_comb':      Variable([ 4.5e5, 5e5, 5.5e5, 6e5, 6.5e5, 7e5, 7.5e5, 8e5, 8.5e5, 9e5, 9.5e5, 1e6, 1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.7e6, 2.5e6], name='x', label=r'$p_{T}$[MeV]'  ),
        'rljet_C1_Beta0p5'        : Regular(20, 0, 1,    name='x', label='$C_{1}^{\beta=0.5}'),
        'rljet_C1_Beta1p2'        : Regular(20, 0, 1,    name='x', label='$C_{1}^{\beta=1.2}'),
        'rljet_C1_Beta1p5'        : Regular(20, 0, 1,    name='x', label='$C_{1}^{\beta=1.5}'),
        'rljet_C1_Beta1p7'        : Regular(20, 0, 1,    name='x', label='$C_{1}^{\beta=1.7}'),
        'rljet_C1_Beta2p0'        : Regular(20, 0, 1,    name='x', label='$C_{1}^{\beta=2.0}'),
        'rljet_C1_Beta2p3'        : Regular(20, 0, 1,    name='x', label='$C_{1}^{\beta=2.3}'),
        'rljet_C2_Beta0p5'        : Regular(20, 0, 1,    name='x', label='$C_{2}^{\beta=0.5}'),
        'rljet_C2_Beta1p2'        : Regular(20, 0, 1,    name='x', label='$C_{2}^{\beta=1.2}'),
        'rljet_C2_Beta1p5'        : Regular(20, 0, 1,    name='x', label='$C_{2}^{\beta=1.5}'),
        'rljet_C2_Beta1p7'        : Regular(20, 0, 1,    name='x', label='$C_{2}^{\beta=1.7}'),
        'rljet_C2_Beta2p0'        : Regular(20, 0, 1,    name='x', label='$C_{2}^{\beta=2.0}'),
        'rljet_C2_Beta2p3'        : Regular(20, 0, 1,    name='x', label='$C_{2}^{\beta=2.3}'),
        'rljet_C3_Beta0p5'        : Regular(20, 0, 1,    name='x', label='$C_{3}^{\beta=0.5}'),
        'rljet_C3_Beta1p2'        : Regular(20, 0, 1,    name='x', label='$C_{3}^{\beta=1.2}'),
        'rljet_C3_Beta1p5'        : Regular(20, 0, 1,    name='x', label='$C_{3}^{\beta=1.5}'),
        'rljet_C3_Beta1p7'        : Regular(20, 0, 1,    name='x', label='$C_{3}^{\beta=1.7}'),
        'rljet_C3_Beta2p0'        : Regular(20, 0, 1,    name='x', label='$C_{3}^{\beta=2.0}'),
        'rljet_C3_Beta2p3'        : Regular(20, 0, 1,    name='x', label='$C_{3}^{\beta=2.3}'),
        'rljet_D2_Beta0p5'        : Regular(20, 0, 4,    name='x', label='$D_{2}^{\beta=0.5}'),
        'rljet_D2_Beta1p2'        : Regular(20, 0, 6,    name='x', label='$D_{2}^{\beta=1.2}'),
        'rljet_D2_Beta1p5'        : Regular(20, 0, 8,    name='x', label='$D_{2}^{\beta=1.5}'),
        'rljet_D2_Beta1p7'        : Regular(20, 0, 10,   name='x', label='$D_{2}^{\beta=1.7}'),
        'rljet_D2_Beta2p0'        : Regular(20, 0, 13,   name='x', label='$D_{2}^{\beta=2.0}'),
        'rljet_D2_Beta2p3'        : Regular(20, 0, 16,   name='x', label='$D_{2}^{\beta=2.3}'),
    }

    var_ecf_beta = {
        'rljet_pt_comb':      Variable([ 4.5e5, 5e5, 5.5e5, 6e5, 6.5e5, 7e5, 7.5e5, 8e5, 8.5e5, 9e5, 9.5e5, 1e6, 1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.7e6, 2.5e6], name='x', label=r'$p_{T}$[MeV]'  ),
        'rljet_ECF2_Beta0p5'      : Regular(20, 0, 1e12, name='x', label='$ECF2_{\beta=0.5}$'),
        'rljet_ECF2_Beta1p2'      : Regular(20, 0, 1e12, name='x', label='$ECF2_{\beta=1.2}$'),
        'rljet_ECF2_Beta1p5'      : Regular(20, 0, 1e12, name='x', label='$ECF2_{\beta=1.5}$'),
        'rljet_ECF2_Beta1p7'      : Regular(20, 0, 1e12, name='x', label='$ECF2_{\beta=1.7}$'),
        'rljet_ECF2_Beta2p0'      : Regular(20, 0, 1e12, name='x', label='$ECF2_{\beta=2.0}$'),
        'rljet_ECF2_Beta2p3'      : Regular(20, 0, 1e12, name='x', label='$ECF2_{\beta=2.3}$'),
        'rljet_ECF3_Beta0p5'      : Regular(20, 0, 1e17, name='x', label='$ECF3_{\beta=0.5}$'),
        'rljet_ECF3_Beta1p2'      : Regular(20, 0, 1e17, name='x', label='$ECF3_{\beta=1.2}$'),
        'rljet_ECF3_Beta1p5'      : Regular(20, 0, 1e17, name='x', label='$ECF3_{\beta=1.5}$'),
        'rljet_ECF3_Beta1p7'      : Regular(20, 0, 1e17, name='x', label='$ECF3_{\beta=1.7}$'),
        'rljet_ECF3_Beta2p0'      : Regular(20, 0, 1e17, name='x', label='$ECF3_{\beta=2.0}$'),
        'rljet_ECF3_Beta2p3'      : Regular(20, 0, 1e17, name='x', label='$ECF3_{\beta=2.3}$'),
    }

    var_dichoric = {
        'rljet_pt_comb':      Variable([ 4.5e5, 5e5, 5.5e5, 6e5, 6.5e5, 7e5, 7.5e5, 8e5, 8.5e5, 9e5, 9.5e5, 1e6, 1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.7e6, 2.5e6], name='x', label=r'$p_{T}$[MeV]'  ),
        'rljet_Dichroic_D2'       : Regular(20, 0, 18,   name='x', label='Dichroic_D2'),
        'rljet_Dichroic_M2'       : Regular(20, 0, 1,    name='x', label='Dichroic_M2'),
        'rljet_Dichroic_N2'       : Regular(20, 0, 1,    name='x', label='Dichroic_N2'),
        'rljet_Dichroic_Tau21_wta': Regular(20, 0, 2,    name='x', label='Dichroic_Tau21_wta'),
        'rljet_Dichroic_Tau32_wta': Regular(20, 0, 4,    name='x', label='Dichroic_Tau32_wta'),
        'rljet_Dichroic_Tau42_wta': Regular(20, 0, 3,    name='x', label='Dichroic_Tau42_wta'),
    }

    var_ecfg = {
        'rljet_pt_comb':      Variable([ 4.5e5, 5e5, 5.5e5, 6e5, 6.5e5, 7e5, 7.5e5, 8e5, 8.5e5, 9e5, 9.5e5, 1e6, 1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.7e6, 2.5e6], name='x', label=r'$p_{T}$[MeV]'  ),
        'rljet_ECFG_2_1'          : Regular(20, 0, 1,    name='x', label='ECFG_2_1'    ),
        'rljet_ECFG_2_1_2'        : Regular(20, 0, 1,    name='x', label='ECFG_2_1_2'  ),
        'rljet_ECFG_3_1'          : Regular(20, 0, 1,    name='x', label='ECFG_3_1'    ),
        'rljet_ECFG_3_1_1'        : Regular(20, 0, 1,    name='x', label='ECFG_3_1_1'  ),
        'rljet_ECFG_3_2'          : Regular(20, 0, 1,    name='x', label='ECFG_3_2'    ),
        'rljet_ECFG_3_2_1'        : Regular(20, 0, 1,    name='x', label='ECFG_3_2_1'  ),
        'rljet_ECFG_3_2_2'        : Regular(20, 0, 1,    name='x', label='ECFG_3_2_2'  ),
        'rljet_ECFG_3_3_1'        : Regular(20, 0, 1,    name='x', label='ECFG_3_3_1'  ),
        'rljet_ECFG_3_3_2'        : Regular(20, 0, 1,    name='x', label='ECFG_3_3_2'  ),
        'rljet_ECFG_4_2'          : Regular(20, 0, 1,    name='x', label='ECFG_4_2'    ),
        'rljet_ECFG_4_2_2'        : Regular(20, 0, 1,    name='x', label='ECFG_4_2_2'  ),
        'rljet_ECFG_4_4_1'        : Regular(20, 0, 1,    name='x', label='ECFG_4_4_1'  ),
    }

    var_main = {
        'rljet_pt_comb':      Variable([ 4.5e5, 5e5, 5.5e5, 6e5, 6.5e5, 7e5, 7.5e5, 8e5, 8.5e5, 9e5, 9.5e5, 1e6, 1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.7e6, 2.5e6], name='x', label=r'$p_{T}$[MeV]'  ),
        'rljet_Angularity'        : Regular(20, 0, 1,    name='x', label='Angularity'),
        'rljet_Aplanarity'        : Regular(20, 0, 1,    name='x', label='Aplanarity'),
        'rljet_C2'                : Regular(20, 0, 1,    name='x', label='$C_{2}$'        ),
        'rljet_D2'                : Regular(20, 0, 6,    name='x', label='$D_{2}$'        ),
        'rljet_Dip12'             : Regular(20, 0, 2,    name='x', label='Dip12'       ),
        'rljet_ECF1'              : Regular(20, 0, 1e7,  name='x', label='ECF1'        ),
        'rljet_ECF2'              : Regular(20, 0, 1e12, name='x', label='ECF2'        ),
        'rljet_ECF3'              : Regular(20, 0, 1e17, name='x', label='ECF3'        ),
        'rljet_FoxWolfram0'       : Regular(20, 0, 1,    name='x', label='FoxWolfram0' ),
        'rljet_FoxWolfram2'       : Regular(20, 0, 1,    name='x', label='FoxWolfram2' ),
        'rljet_KtDR'              : Regular(20, 0, 6,    name='x', label='KtDR'        ),
        'rljet_L1'                : Regular(20, 0, 1,    name='x', label='$L_{1}$'     ),
        'rljet_L2'                : Regular(20, 0, 1,    name='x', label='$L_{2}$'     ),
        'rljet_L3'                : Regular(20, 0, 1,    name='x', label='$L_{3}$'     ),
        'rljet_L4'                : Regular(20, 0, 5,    name='x', label='$L_{4}$'     ),
        'rljet_L5'                : Regular(20, 0, 1,    name='x', label='$L_{5}$'     ),
        'rljet_M2'                : Regular(20, 0, 1,    name='x', label='$M_{2}$'     ),
        'rljet_Mu12'              : Regular(20, 0, 1,    name='x', label='Mu12'        ),
        'rljet_N2'                : Regular(20, 0, 1,    name='x', label='$N_{2}$'          ),
        'rljet_N3'                : Regular(20, 0, 6,    name='x', label='$N_{3}$'          ),
        'rljet_PlanarFlow'        : Regular(20, 0, 1,    name='x', label='PlanarFlow'  ),
        'rljet_Qw'                : Regular(20, 0, 1e6,  name='x', label='$Q_{w}$'          ),
        'rljet_Sphericity'        : Regular(20, 0, 1,    name='x', label='Sphericity'  ),
        'rljet_Split12'           : Regular(20, 0, 1e6,  name='x', label='Split12'     ),
        'rljet_Split23'           : Regular(20, 0, 1e6,  name='x', label='Split23'     ),
        'rljet_Split34'           : Regular(20, 0, 1e6,  name='x', label='Split34'     ),
        'rljet_Tau1_wta'          : Regular(20, 0, 1,    name='x', label='$\tau_{1}'    ),
        'rljet_Tau2_wta'          : Regular(20, 0, 1,    name='x', label='$\tau_{2}'    ),
        'rljet_Tau32_wta'         : Regular(20, 0, 1,    name='x', label='$\tau_{32}'   ),
        'rljet_Tau3_wta'          : Regular(20, 0, 1,    name='x', label='$\tau_{3}'    ),
        'rljet_Tau42_wta'         : Regular(20, 0, 1,    name='x', label='$\tau_{42}'   ),
        'rljet_Tau4_wta'          : Regular(20, 0, 1,    name='x', label='$\tau{4}$'    ),
        'rljet_ThrustMaj'         : Regular(20, 0, 1,    name='x', label='ThrustMaj'   ),
        'rljet_ThrustMin'         : Regular(20, 0, 1,    name='x', label='ThrustMin'   ),
        'rljet_ZCut12'            : Regular(20, 0, 1,    name='x', label='ZCut12'      ),
        'rljet_n_constituents'    : Regular(20, 0, 200,  name='x', label='$n_{const.}$'),
        'rljet_ungroomed_ntrk500' : Regular(20, 0, 100,  name='x', label='$N_{trk,500}$' ),
    }

    fail, broken = [], []
    hists = {}
    samples = sorted(samples_DXAOD.keys())
    samples = [x for x in samples if not 'gamma' in x]
    exec('variables = var_'+sys.argv[1])
    # Load in samples
    for samp in samples:
        if not sys.argv[2] in samp: continue
        #if os.path.exists(sys.argv[1]+'_'+samp+'.pkl'):
        #    print('Loading file', sys.argv[1]+'_'+samp+'.pkl')
        #    with open(sys.argv[1]+'_'+samp+'.pkl', 'rb') as file:
        #        hists[samp] = pkl.load(file)
        #else:
        _files, _fail, _broken = load_files(samp, folder, vnames=list(variables.keys()))
        fail   += _fail
        broken += _broken
        _hists = get_sample_histos(_files, list(variables.values()), list(variables.keys()))
        _hists = reduce_histos(_hists, samp)
        hists[samp] = _hists
        del _hists
        del _files
        print('Saving to file', sys.argv[1]+'_'+samp+'.pkl')
        with open(sys.argv[1]+'_'+samp+'.pkl', 'wb') as file:
            pkl.dump(hists[samp], file, protocol=pkl.HIGHEST_PROTOCOL)

    TAGGERS = ['dnn_cont_50', 'dnn_cont_80', 'dnn_incl_50', 'dnn_incl_80']#, 'w_50', 'w_80']
    for vname, var in variables.items():
        print('Plotting', vname)
        for tag in TAGGERS+['all']:
            print('\t', tag)
            data   = hists['data_2015'][vname][tag] + \
                     hists['data_2016'][vname][tag] + \
                     hists['data_2017'][vname][tag] + \
                     hists['data_2018'][vname][tag]

            wjets  = hists['sherpa_wjets_mc16a'][vname][tag] + \
                     hists['sherpa_wjets_mc16d'][vname][tag] + \
                     hists['sherpa_wjets_mc16e'][vname][tag]

            zjets  = hists['sherpa_zjets_mc16a'][vname][tag] + \
                     hists['sherpa_zjets_mc16d'][vname][tag] + \
                     hists['sherpa_zjets_mc16e'][vname][tag]

            ttbar  = hists['ttbar_allhad_mc16a'][vname][tag] + \
                     hists['ttbar_allhad_mc16d'][vname][tag] + \
                     hists['ttbar_allhad_mc16e'][vname][tag]

            pythia = hists['pythia_dijet_mc16a'][vname][tag] + \
                     hists['pythia_dijet_mc16d'][vname][tag] + \
                     hists['pythia_dijet_mc16e'][vname][tag]

            sherpa = hists['sherpa_alt_dijet_mc16a'][vname][tag] + \
                     hists['sherpa_alt_dijet_mc16d'][vname][tag] + \
                     hists['sherpa_alt_dijet_mc16e'][vname][tag]

            lund   = hists['sherpa_lund_dijet_mc16a'][vname][tag] + \
                     hists['sherpa_lund_dijet_mc16d'][vname][tag] + \
                     hists['sherpa_lund_dijet_mc16e'][vname][tag]

            dipole = hists['herwig_dipole_dijet_mc16a'][vname][tag] + \
                     hists['herwig_dipole_dijet_mc16d'][vname][tag] + \
                     hists['herwig_dipole_dijet_mc16e'][vname][tag]

            ang    = hists['herwig_angular_dijet_mc16a'][vname][tag] + \
                     hists['herwig_angular_dijet_mc16d'][vname][tag] + \
                     hists['herwig_angular_dijet_mc16e'][vname][tag]

            plot_1d(vname, tag, data=data,
                                wjets=wjets,
                                zjets=zjets,
                                ttbar=ttbar,
                                pythia=pythia)

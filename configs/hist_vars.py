from hist.axis import Variable, Regular

var_main = {
    #'rljet_pt_comb':      Variable([ 4.5e5, 5e5, 5.5e5, 6e5, 6.5e5, 7e5, 7.5e5, 8e5, 8.5e5, 9e5, 9.5e5, 1e6, 1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.7e6, 2.5e6], name='x', label=r'$p_{T}$[MeV]'  ),
    'rljet_pt_comb':            Regular(20, 300e3, 600e3, name='x', label=r'$p_{T}$[MeV]'  ),
    'rljet_m_comb[:,0]'       : Regular(20, 50e3, 500e3,  name='x', label='m [MeV]'),
    'rljet_Angularity'        : Regular(20, 0., 0.1,  name='x', label='Angularity'),
    'rljet_Aplanarity'        : Regular(20, 0., 1,    name='x', label='Aplanarity'),
    'rljet_C2'                : Regular(20, 0., 1,    name='x', label=r'$C_{2}$'        ),
    'rljet_D2'                : Regular(20, 0., 6,    name='x', label=r'$D_{2}$'        ),
    'rljet_Dip12'             : Regular(20, 0., 2,    name='x', label='Dip12'       ),
    'rljet_ECF1'              : Regular(20, 0., 1e7,  name='x', label='ECF$_{1}$'   ),
    'rljet_ECF2'              : Regular(20, 0., 1e12, name='x', label='ECF$_{2}$'   ),
    'rljet_ECF3'              : Regular(20, 0., 1e17, name='x', label='ECF$_{3}$'   ),
    'rljet_FoxWolfram0'       : Regular(20, 0., 1,    name='x', label='FoxWolfram0' ),
    'rljet_FoxWolfram2'       : Regular(20, 0., 1,    name='x', label='FoxWolfram2' ),
    'rljet_KtDR'              : Regular(20, 0., 6,    name='x', label='KtDR'        ),
    'rljet_Mu12'              : Regular(20, 0., 1,    name='x', label='Mu12'        ),
    'rljet_L1'                : Regular(20, 0., 1,    name='x', label='$L_{1}$'     ),
    'rljet_L2'                : Regular(20, 0., 1,    name='x', label='$L_{2}$'     ),
    'rljet_L3'                : Regular(20, 0., 1,    name='x', label='$L_{3}$'     ),
    'rljet_L4'                : Regular(20, 0., 5,    name='x', label='$L_{4}$'     ),
    'rljet_N2'                : Regular(20, 0., 1,    name='x', label='$N_{2}$'          ),
    'rljet_PlanarFlow'        : Regular(20, 0., 2,    name='x', label='PlanarFlow'  ),
    'rljet_Qw'                : Regular(20, 0., 1e6,  name='x', label=r'$Q_{w}$'          ),
    'rljet_Sphericity'        : Regular(20, 0., 1,    name='x', label='Sphericity'  ),
    'rljet_Split12'           : Regular(20, 0., 1e6,  name='x', label='$sqrt{12}$'     ),
    'rljet_Split23'           : Regular(20, 0., 1e6,  name='x', label='$sqrt{23}$'     ),
    'rljet_Split34'           : Regular(20, 0., 1e6,  name='x', label='$sqrt{34}$'     ),
    'rljet_Tau1_wta'          : Regular(20, 0., 1,    name='x', label=r'$\tau_{1}$'    ),
    'rljet_Tau2_wta'          : Regular(20, 0., 1,    name='x', label=r'$\tau_{2}$'    ),
    'rljet_Tau32_wta'         : Regular(20, 0., 1,    name='x', label=r'$\tau_{32}$'   ),
    'rljet_Tau3_wta'          : Regular(20, 0., 1,    name='x', label=r'$\tau_{3}$'    ),
    'rljet_Tau42_wta'         : Regular(20, 0., 1,    name='x', label=r'$\tau_{42}$'   ),
    'rljet_Tau4_wta'          : Regular(20, 0., 1,    name='x', label=r'$\tau{4}$'    ),
    'rljet_ThrustMaj'         : Regular(20, 0., 1,    name='x', label='ThrustMaj'   ),
    'rljet_ThrustMin'         : Regular(20, 0., 1,    name='x', label='ThrustMin'   ),
    'rljet_ZCut12'            : Regular(20, 0., 1,    name='x', label='ZCut12'      ),
    'rljet_n_constituents'    : Regular(20, 0., 200,  name='x', label=r'$n_{const.}$'),
    'rljet_ungroomed_ntrk500' : Regular(20, 0., 100,  name='x', label=r'$N_{trk,500}$' ),
}

var_series = {
    'rljet_L1'                : Regular(20, 0., 1,    name='x', label='$L_{1}$'     ),
    'rljet_L2'                : Regular(20, 0., 1,    name='x', label='$L_{2}$'     ),
    'rljet_L3'                : Regular(20, 0., 1,    name='x', label='$L_{3}$'     ),
    'rljet_L4'                : Regular(20, 0., 5,    name='x', label='$L_{4}$'     ),
    'rljet_L5'                : Regular(20, 0., 1,    name='x', label='$L_{5}$'     ),
    'rljet_M2'                : Regular(20, 0., 1,    name='x', label='$M_{2}$'     ),
    'rljet_N2'                : Regular(20, 0., 1,    name='x', label='$N_{2}$'          ),
    'rljet_N3'                : Regular(20, 0., 6,    name='x', label='$N_{3}$'          ),
}

var_beta = {
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
    'rljet_Dichroic_D2'       : Regular(20, 0, 18,   name='x', label='Dichroic_D2'),
    'rljet_Dichroic_M2'       : Regular(20, 0, 1,    name='x', label='Dichroic_M2'),
    'rljet_Dichroic_N2'       : Regular(20, 0, 1,    name='x', label='Dichroic_N2'),
    'rljet_Dichroic_Tau21_wta': Regular(20, 0, 2,    name='x', label='Dichroic_Tau21_wta'),
    'rljet_Dichroic_Tau32_wta': Regular(20, 0, 4,    name='x', label='Dichroic_Tau32_wta'),
    'rljet_Dichroic_Tau42_wta': Regular(20, 0, 3,    name='x', label='Dichroic_Tau42_wta'),
}

var_ecfg = {
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

var_2d = {
    'rljet_pt_comb_2D_rljet_log_m_pt':
    (
    Variable([ 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300, 1400, 1500, 1700, 2500, ], name='x', label=r'$p_{T}$[GeV]'  ),
    Variable([ -4., -2., -1.6, -1.4, -1.2, -1., -0.8, -0.7, -0.6, -0.55, -0.5, 0. ], name='y', label=r'$log(m/p_{T})$'),
    )
}

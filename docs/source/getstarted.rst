===============
Getting Started
===============
.. _getting_started:

How to run 
----------

To run a configuration file, you should use the provided CLI for now (again this will change once an API is more mature) -- if package was installed correctly you can run

.. code-block:: python

    pythium-sklim -c <sklim-config.py>

for sklimming configs, or 

.. code-block:: python

    pythium-hist -c <sklim-config.py>

for histogramming configs. 

Getting your data ready (Pending dev....)
-----------------------------------------

If you have some `ROOT` NTuple you would like to use to follow along, please do and skip this part! 
Otherwise, you can use (not yet!) our dummy Ntuple generator by executing in your terminal

.. code-block:: bash

    make-dummy-ntup --options

which will execute the script `misc/make_dummy_file.py` and produce the following output
files 

* my_foo_bkg.root
* my_bar_bkg.root
* my_alt_bar_bkg.root (identical structure to `my_bar_bkg.root`)
* my_cool_sig.root
* my_scary_data.root

in your current directory under `./ntups/` (or the output directory you specified in `--options`). 
Feel free to explore the data using interactive python + `uproot` or `uproot-browser`.
The non-data files content is as follow:

::

    my_foo_bkg
    ├── nominal
    │   ├─ jets_pt
    │   ├─ njets
    │   ├─ mc_weight
    │   ├─ weight_var_up 
    │   ├─ weight_var_down
    ├── common_bkg_tree_var_up
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── common_bkg_tree_var_down  
    ├── ├─ jets_pt
    │   ├─ njets    
    ├── common_mc_tree_var_up
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── common_mc_tree_var_down
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── foo_bkg_tree_var_up
    ├── ├─ jets_pt
    │   ├─ njets
    ├── foo_bkg_tree_var_down
    ├── ├─ jets_pt
    │   ├─ njets

::

    my_bar_bkg
    ├── nominal
    │   ├─ jets_pt
    │   ├─ njets
    │   ├─ mc_weight
    │   ├─ weight_var_up 
    │   ├─ weight_var_down
    ├── common_bkg_tree_var_up
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── common_bkg_tree_var_down  
    ├── ├─ jets_pt
    │   ├─ njets    
    ├── common_mc_tree_var_up
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── common_mc_tree_var_down
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── bar_bkg_tree_var_up
    ├── ├─ jets_pt
    │   ├─ njets
    ├── bar_bkg_tree_var_down
    ├── ├─ jets_pt
    │   ├─ njets



::

    my_cool_sig
    ├── nominal
    │   ├─ jets_pt
    │   ├─ njets
    │   ├─ mc_weight
    │   ├─ weight_var_up 
    │   ├─ weight_var_down
    ├── common_mc_tree_var_up
    ├── ├─ jets_pt
    ├── ├─ njets
    ├── common_mc_tree_var_down
    ├── ├─ jets_pt
    ├── ├─ njets

while the data file simply looks like:

::

    my_scary_data
    ├── nominal
    │   ├─ jets_pt
    │   ├─ njets


Your first Pythium workflow
---------------------------
Sklimming
~~~~~~~~~~~~~~~~~~~~~~~~~
You can start now with pre-processing your data; in this case there is not much pre-processing
to-do, but imaging your NTuples contain many many more variables and trees. 


To do this, we build our pre-processing config. Open a new file `configs/sklim.py` and copy the 
following lines

.. code-block:: python
    
    # ===== Import statements  =========================
    from pythium.common.samples import Sample
    from pythium.common.branches import Branch
    from pythium.common.selection import Selection


    # ===== General Settings  =========================
    general_settings = {}
    general_settings['JobName'] = 'my_first_pythium'
    general_settings['OutDir'] = './my_first_pythium/sklimmed/'
    general_settings['SkipMissingFiles'] = True
    general_settings['DumpToFormat'] = 'parquet'


    # ===== Branches Settings  =========================

    def crazy_pt(jet0_pt, ):
        jet0_pt = jet0_pt**2 + 10
        return jet0_pt

    branches = [ 
                Branch('njets', 'njets'), # You can just retrieve branches
                Branch('mcweight', 'mc_weight'),
                Branch('jets0_pt', lambda pt: ak.mask(pt, ak.num(pt,axis=1) > 0)[:,0], args = ['jets_pt']), # You can create new branches
                Branch('crazy_jets0_pt', crazy_pt, args = ['jets0_pt'],), # You can use Branches you just created
                Branch('weight_var_up', 'weight_var_up'),
                Branch('weight_var_down', 'weight_var_down'),
            ]

    data_branches = [br for br in branches if br.name in ['mcweight', 'weight_var_up', 'weight_var_down']]
    nominal_only_branches = [br for br in branches if br.name in ['weight_var_up', 'weight_var_up']]
    
    # ==== Assign trees to branches =================
    
    data_trees = ['nominal']
    sig_trees = data_trees+ ['common_mc_tree_var_up', 'common_mc_tree_var_down']
    bkg_trees =  ['common_bkg_tree_var_up','common_bkg_tree_var_down']
    foo_bkg_trees = sig_trees + bkg_trees + ['foo_bkg_tree_var_up','foo_bkg_tree_var_down']
    bar_bkg_trees = sig_trees + bkg_trees + ['bar_bkg_tree_var_up','bar_bkg_tree_var_down']

    data_branches, sig_branches, foo_bkg_branches, bar_bkg_branches = {}, {}, {}, {}

    for tree in data_trees: data_branches[tree] = data_branches

    for tree in sig_trees:
        if tree != 'nominal':
            keep_brs = [br for br in branches if br not in nominal_only_branches]
            sig_branches[tree] = keep_brs
        else:
            sig_branches[tree] = branches

    for tree in foo_bkg_trees:
        if tree != 'nominal':
            keep_brs = [br for br in branches if br not in nominal_only_branches]
            foo_bkg_branches[tree] = keep_brs
        else:
            foo_bkg_branches[tree] = branches

    for tree in bar_bkg_trees:
        if tree != 'nominal':
            keep_brs = [br for br in branches if br not in nominal_only_branches]
            bar_bkg_branches[tree] = keep_brs
        else:
            bar_bkg_branches[tree] = branches


    # ==== Specify samples =================
    samples_dir = './ntups/'  # this can be a list of places to look
    samples = [
                Sample('signal', tag = ['cool'], where = samples_dir, branches = sig_branches),
                Sample('foo_bkg', tag = ['foo'], where = samples_dir, branches = foo_bkg_branches),
                Sample('bar_bkg', tag = ['bar'], where = samples_dir, branches = bar_bkg_branches),
                Sample('alt_bar_bkg', tag = ['alt_bar'], where = samples_dir, branches = bar_bkg_branches),
                Sample('data', tag = ['scary'], where = samples_dir, branches = data_branches, isdata = True )
                ]

Try and go through this config to understand what we've done -- the API is meant to use familiar terms !

1. We started first by importing the useful API pieces to write the config
2. We specified our general Settings (e.g. where to save out pre-processed files, what format should output be, etc). More information on the avaialble settings and their meaning is in :doc:`configs`
3.  We specified a general list of branches/variables that we want to grab from our inputs. Then a subset of branches is specified that are special for data samples (e.g. no weights)
4. We then made a mapping from trees to branches to grab from those trees for each of the samples. In this particular example we needed mappings for all samples, but often many samples will share the trees and branches that need to be collected and so we would not need to be so verbose
5. Finally, we specified the list of samples we want, gave them a name, an identifier (`tag`), where to find them and the trees-branches mapping for the sample


Notice that in this setup, there is at least 3 required python objects:

* A `list` called `samples`
* A `dict` called `general_settings`
* A `list` called `branches` ??


In order to start pre-processing, just execute the following line 

.. code-block:: bash 

    pythium-sklim --cfg ./configs/sklim.py


If you look inside the output directory `./my_first_pythium/`, you should see the following files:

Signal files:

* signal_nominal.parquet
* signal_common_mc_tree_var_up.parquet
* signal_common_mc_tree_var_down.parquet

Background files:

* foo_bkg_nominal.parquet
* etc...

Data files:

* data_nominal.parquet

Histogramming
~~~~~~~~~~~~~~~~~~~~~~~~~

We will now use the pre-processed data to make some histograms. For that we need a new config file `configs/histogram.py`
Open this file and copy the following:

.. code-block:: python
    
    # ===== Import statements  =========================
    from pythium.histogramming.objects import ( Observable, 
                                                Region, 
                                                TreeSyst, WeightSyst, )
    from pythium.histogramming.binning import RegBin, VarBin
    # ===========================================
    # ================= Settings ================
    # ===========================================
    general = {}
    general['OutDir'] = './my_first_pythium/hist/'
    general['inDir']  = ["./my_first_pythium/sklimmed/"]
    general['inFormat']  = 'parquet'
    general['FromPythium']  = True
    general['dask']  = False
    # ===========================================
    # ================= Samples ================
    # ===========================================    
    from configs.tth_ICvSM_config import samples
    # ===========================================
    # =============== Observables ===============
    # ===========================================
    observables = [
                    Observable(var = 'jets0_pt', name = 'jet_pt', binning = RegBin(0,300,20), dataset = 'nominal'),
                    Observable.fromFunc(name = 'pt_sq_func', lambda pt: pt**2, ['jets0_pt'], binning = RegBin(0,90e3,400), dataset = 'nominal'),
                    Observable.fromStr(name = 'pt_sq_str', 'jets0_pt**2', binning = RegBin(0,90e3,400), dataset = 'nominal')
                  ]
    

    # ===========================================
    # ================= Regions =================
    # ===========================================
    inclusive = Selection(lambda h_pt: h_pt>=0, args = ['jets0_pt'], )
    signal_region = Selection(lambda h_pt: h_pt>=10, args = ['jets0_pt'], )
    control_region = Selection.fromStr('jets0_pt>100' )

    regions = [
                Region(name = 'Inclusive', selection = inclusive),
                Region(name = 'SR', selection = signal_region),
                Region(name = 'CR', selection = control_region),
            ]


    systematics = [
                    TreeSyst("common_bkg_tree_var", 'shapenorm', 
                            up = 'common_bkg_tree_var_up', 
                            down = 'common_bkg_tree_var_down', 
                            exclude_samples = ['signal', 'data']), 
                    
                    TreeSyst("common_mc_tree", 'shapenorm', 
                            up = 'common_mc_tree_var_up', 
                            down = 'common_mc_tree_var_down', 
                            exclude_samples = ['data']), 
                    
                    TreeSyst("bar_bkg_tree", 'shapenorm', 
                            up = 'bar_bkg_tree_var_up', 
                            down = 'bar_bkg_tree_var_down', 
                            samples = ['bar_bkg']), 
                    
                    TreeSyst("foo_bkg_tree", 'shapenorm', 
                            up = 'foo_bkg_tree_var_up', 
                            down = 'foo_bkg_tree_var_down', 
                            samples = ['foo_bkg']), 
                    
                    NTupSyst("bar_vs_alt_bar", 'shapenorm', up = 'alt_bar', symmetrize= True),
                    
                    WeightSyst("weight_syst", 'shapenorm', up = 'weight_var_up', down = 'weight_var_down')
                    
                    WeightSyst.fromFunc("weight_syst_sq", 'shapenorm', 
                                        up = dict(func=lambda x : x**2, args = ['weight_var_up']), 
                                        down = dict(func=lambda x : x**2, args = ['weight_var_down']),
                                        exclude_samples = ['data']
                                        )
                    WeightSyst.fromStr("weight_syst_sq_str", 'shapenorm', up = 'weight_var_up**2', down = 'weight_var_down**2')
                    ]

and now we say something about histogramming

Plotting
~~~~~~~~~

.. WAIT FOR JOSHS INPUT
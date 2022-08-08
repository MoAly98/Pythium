# Python Imports
import logging
import pathlib
from unittest import mock
import unittest
import os
import re
# Scikit 
import hist
from hist import Hist
import numpy as np

# Pythium Imports
from pythium.histogramming import processor
from pythium.histogramming.binning import _Binning
from pythium.common.samples import Sample
from pythium.histogramming.objects import Region,  Systematic, Observable, CrossProduct
from pythium.common.selection import Selection
from pythium.histogramming.managers import _TaskManager, _InputManager


test_dir = os.path.dirname(os.path.abspath(__file__))


class TestProcessor():

    def test_Processor(self):
        
        mock_observable_instance = Observable('observable','observable', _Binning([0., 1.]), dataset = 'tree')
        mock_region_instance = Region('region',Selection(lambda x: x, ['cut_on']))
        mock_syst_instance = Systematic('syst', 'SHAPENORM' , 'up' )
        mock_sample_instance = Sample('sample', 'tag', '/path/to/ntuples/', {})
        processor_instance = processor.Processor( samples = [mock_sample_instance], 
                                                  regions = [mock_region_instance], 
                                                  systematics = [mock_syst_instance],
                                                  observables = [mock_observable_instance],
                                                  general = {'outdir': '/path/to/output',},
                                                  scheduler = 'synchronous',
                                                )
        assert processor_instance.samples     == [mock_sample_instance]
        assert processor_instance.regions     == [mock_region_instance]
        assert processor_instance.systematics == [mock_syst_instance]
        assert processor_instance.observables == [mock_observable_instance]
        assert processor_instance.general_settings     == {'outdir': '/path/to/output',}
        assert processor_instance.scheduler   == 'synchronous'


    def test_processor_create(self,):

        # Prepare object instances to run a processor
        mock_observable_instance = Observable('observable','observable', _Binning([0., 1.]), dataset = 'tree')
        mock_region_instance = Region('region',Selection(lambda x: x, ['cut_on']))
        mock_syst_instance = Systematic('syst', 'SHAPENORM' , 'up' )
        mock_sample_instance = Sample('sample', 'tag', '/path/to/ntuples/', {})
        
        processor_instance = processor.Processor( samples =     [mock_sample_instance], 
                                                  regions =     [mock_region_instance], 
                                                  systematics = [mock_syst_instance],
                                                  observables = [mock_observable_instance],
                                                  general = { 'indir': [f'./tests/histogramming/data/'],
                                                               'frompythium': True,
                                                               'informat': 'parquet',
                                                               'samplesel': False,
                                                               'outdir': 'x'
                                                            },
                                                  scheduler = 'synchronous',
                                                )

        xps = list(processor_instance.cross_product( processor_instance.samples, 
                                                     processor_instance.regions, 
                                                     processor_instance.systematics, 
                                                     processor_instance.observables
                                                    ))
        processor_instance.create()

        # ======================= Build expectation =============================
        expected_dependencies = {
                                 '_get_data': set(), 
                                 '_create_variables': {'_get_data'}, 
                                 '_apply_cut': {'_create_variables'}, 
                                 '_get_var': {'_apply_cut'}, 
                                 '_get_weights': {'_apply_cut'}, 
                                 '_make_histogram': {'_get_weights', '_get_var'},
                                 'sum': {'_make_histogram'}}
        mock_xps = [
                    CrossProduct(mock_sample_instance,mock_region_instance,mock_observable_instance,mock_syst_instance,'up'),
                    CrossProduct(mock_sample_instance,mock_region_instance,mock_observable_instance,None,'nom'),
                    ]
        # ======================= Assertions =============================
        assert len(processor_instance.graph)  == 2
        assert len(processor_instance.xps) == 2
        assert sorted(processor_instance.xps) == sorted(mock_xps)
        
        for i, job in enumerate(processor_instance.graph):
            assert sorted(remove_tokens(job.__dask_graph__().dependencies)) == sorted(expected_dependencies)
    
    def test_processor_run(self,tmpdir):
        
        mock_observable_instance = Observable('observable1','observable1', _Binning([0., 1.]), dataset = 'tree')
        mock_region_instance = Region('region',Selection.fromStr('observable1!=-99'))
        mock_syst_instance = Systematic('syst', 'SHAPENORM' , 'up' )
        mock_sample_instance = Sample('sample', 'tag', '/path/to/ntuples/', {})
        processor_instance = processor.Processor( samples =     [mock_sample_instance], 
                                                  regions =     [mock_region_instance], 
                                                  systematics = [mock_syst_instance],
                                                  observables = [mock_observable_instance],
                                                  general = { 'indir': [f'./tests/histogramming/data/'],
                                                               'frompythium': True,
                                                               'informat': 'parquet',
                                                               'samplesel': False,
                                                               'outdir': tmpdir
                                                            },
                                                  scheduler = 'synchronous',
                                                )
        xps = list(processor_instance.cross_product( processor_instance.samples, 
                                                     processor_instance.regions, 
                                                     processor_instance.systematics, 
                                                     processor_instance.observables
                                                    ))
        processor_instance.create()
        observable_uid_hist = processor_instance.run()

        # ======================= Build expectation =============================
        h = Hist( hist.axis.Variable([0,1], overflow=True, underflow=True,), 
                  name = "observable1", 
                  storage = hist.storage.Weight())
        
        # tests/histogramming/data/create_parquet.py creates sample_tree and sample_tree2          
        # Filling from 2 files, so fill twice
        h.fill(np.arange(10))
        h.fill(np.arange(10))
    
        expected_result = {
            'observable1':   {'sample_region_syst_up': h,
                              'sample_region_nom': h}
            }
        
        # ======================= Assertions =============================
        assert expected_result == dict(observable_uid_hist)
        for obs, combo_to_hist in observable_uid_hist.items():
            assert all('down' not in k for k in list(dict(combo_to_hist).keys()))

def remove_tokens(dask_depend):
    clean_dask_dep = {}
    for k, v in dask_depend.items():
        clean_key = re.sub('(-.*)+', '', k)
        clean_set = {re.sub('(-.*)+', '', s) for s in v}
        clean_dask_dep[clean_key] = clean_set
    
    return clean_dask_dep

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(parentdir)

sys.path.append(parentdir)
sys.path.append(parentparentdir)
from pythium.histogramming.processor import Processor
import pythium.histogramming as hist
cfg_path = '/Users/moaly/Work/phd/pythium/Pythium/configs/StreamlineHistogrammingConfig.py'

cfg = hist.config.Config(cfg_path).process()

processor = hist.processor.Processor(cfg)
samples =  processor.cfg["samples"]
regions = processor.cfg["regions"]
systematics = processor.cfg["systematics"]
observables = processor.cfg["observables"]

xps = processor.cross_product(samples, regions, systematics, observables)
for xp in xps:
    sample, region, obs, syst, template = xp
    if syst is not None:
        paths = processor.get_input_files(sample, obs, syst, template)
        if sample.name == 'TTH_ICt' and obs.dataset == 'tth_observables' and syst.name == 'FakeTreeVar' and template == 'up':
            assert paths == ['/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/TTH_ICt_chunk0_treevar_UP.parquet']
        if sample.name == 'TTH_ICt' and obs.dataset == 'tth_observables' and syst.name == 'FakeTreeVar' and template == 'down':
            assert paths == ['/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/TTH_ICt_chunk0_treevar_DOWN.parquet']
        if sample.name == 'TTH_ICt' and obs.dataset == 'tth_observables' and syst.name == 'FakeNtupVar' and template == 'up':
            assert paths == ['/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/alt_sample_chunk0_tth_observables.parquet'] 
        if sample.name == 'TTH_ICt' and obs.dataset == 'tth_observables' and syst.name == 'FakeNtupVar' and template == 'down':
            assert paths == ['/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/alt_sample_chunk0_tth_observables.parquet']  
        if sample.name == 'TTH_ICt' and obs.dataset == 'tth_observables' and syst.name == 'FakeNtupVar' and template == 'nom':
            assert paths == ['/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/TTH_ICt_chunk0_tth_observables.parquet']    



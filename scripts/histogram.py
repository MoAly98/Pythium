#============== System and Python Imports
import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
#============ thbbanalysis Imports
import utils.histogramming as hist
from utils.common import tools
#=========== Pythonic Imports 
import numpy as np
cfg_path = '/Users/moaly/Work/phd/pythium/Pythium/configs/StreamlineHistogrammingConfig.py'

cfg = hist.config.Config(cfg_path).process()
procer = hist.processor.Processor(cfg)
procer.create()
hists_dict = procer.run()
procer.save(hists_dict)


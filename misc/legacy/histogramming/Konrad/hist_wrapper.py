import os
import sys
import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess


class Histogram_wrapper(hist.basehist.BaseHist, family=hist):
    # looks like I will need to update python version, name and label are not supported in hist 2.4 
    def __init__(self, *args, storage = None, metadata = None, data = None,name = None, label = None):
        
        super().__init__(*args, storage = None, metadata = None, data = None)
        


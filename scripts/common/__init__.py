
import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(os.path.dirname(parentdir))
from misc.logo import make_header
make_header()

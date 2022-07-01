from setuptools import setup

setup(install_requires = [
    "boost_histogram>=1.0.2",
    "awkward>=1.0",
    "uproot>=4.0",
    "mplhep",
    "numpy",
    "h5py==3.6.0"
    "psutil", # To remove
    "beartype", # To remove
])
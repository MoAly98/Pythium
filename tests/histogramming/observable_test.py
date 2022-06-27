import os,sys
from inspect import getsource
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils.histogramming.objects import Observable, ObservableBuilder, Binning, RegBin, VarBin

observable = Observable("X", "Y", RegBin(low=0, high=1000, nbins = 50), 'nominal_Loose')

assert observable.var == "X"
assert observable.name == "Y"

assert isinstance(observable.binning, list)
for axbin in observable.binning:
    assert axbin.min == 0
    assert axbin.max == 1000
    assert axbin.nbins == 50
assert observable.dataset == 'nominal_Loose'

new_observable = Observable.fromFunc( "Y**2", lambda x: x**2, ["x"],
                                     RegBin(low=0, high=1000**2, nbins = 500), 
                                     'nominal_Loose')

assert new_observable.var == "Y**2"
assert new_observable.name == "Y**2"

assert isinstance(new_observable.binning, list)
for axbin in new_observable.binning:
    assert axbin.min == 0
    assert axbin.max == 1000**2
    assert axbin.nbins == 500
assert new_observable.dataset == 'nominal_Loose'

assert new_observable.builder.func(2) == 4
assert new_observable.builder.func(2) == ObservableBuilder(lambda x: x**2,  ["x"], ).func(2)

new_observable_fromstr = Observable.fromStr( "Z**2", "z**2",
                                              RegBin(low=0, high=1000**2, nbins = 500), 
                                              'nominal_Loose')

assert new_observable_fromstr.var == "Z**2"
assert new_observable_fromstr.name == "Z**2"

assert isinstance(new_observable_fromstr.binning, list)
for axbin in new_observable.binning:
    assert axbin.min == 0
    assert axbin.max == 1000**2
    assert axbin.nbins == 500
assert new_observable_fromstr.dataset == 'nominal_Loose'
import pickle
import matplotlib.pyplot as plt
f = "tests/histogramming/histograms/top_pt.pkl"
f2 = "tests/histogramming/histograms_nonsync/top_pt.pkl"
with open(f, 'rb') as file:
    hdict = pickle.load(file)
with open(f2, 'rb') as file2:
    hdict2 = pickle.load(file2)
plothist = lambda h: plt.bar(*h.axes.centers, h.values(), width=h.axes.widths[0])


h =  hdict['TTH_ICt_Inclusive_nom']

print(h.values())
plothist(h)
plt.show()

h2 =  hdict2['TTH_ICt_Inclusive_nom']
print(h.values())
plothist(h2)
plt.show()
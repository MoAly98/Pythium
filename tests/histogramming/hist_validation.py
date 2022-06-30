import pickle
import matplotlib.pyplot as plt
f = "tests/histogramming/histograms/top_pt.pkl"
f2 = "tests/histogramming/histograms_nonsync/top_pt.pkl"
f3 = "tests/histogramming/histograms_nonsync/top_pt_eta.pkl"

with open(f, 'rb') as file:
    hdict = pickle.load(file)
with open(f2, 'rb') as file2:
    hdict2 = pickle.load(file2)
with open(f3, 'rb') as file3:
    hdict3 = pickle.load(file3)

plothist = lambda h: plt.bar(*h.axes.centers, h.values(), width=h.axes.widths[0])
plot2d = lambda h: plt.pcolormesh(*h.axes.edges.T, h.values().T)

h =  hdict['TTH_ICt_Inclusive_nom']

print(h.values())
plothist(h)
plt.show()

h2 =  hdict2['TTH_ICt_Inclusive_nom']
print(h2.values())
plothist(h2)
plt.show()


h3 =  hdict3['TTH_ICt_Inclusive_nom']
print(h3.values())
plot2d(h3)
plt.show()
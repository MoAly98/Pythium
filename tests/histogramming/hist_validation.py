import pickle
import matplotlib.pyplot as plt
f = "tests/histogramming/histograms/top_pt.pkl"
with open(f, 'rb') as file:
    hdict = pickle.load(file)

h =  hdict['TTH_ICt_Inclusive_nom'][0]
plothist = lambda h: plt.bar(*h.axes.centers, h.values(), width=h.axes.widths[0])
print(h.values())
plothist(h)
plt.show()
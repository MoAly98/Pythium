import numpy as np
import matplotlib.pyplot as plt

def make_toy(distribution = 'non_cent_chi2', peak = 30, ):
    if distribution == 'non_cent_chi2':
        toy = np.random.noncentral_chisquare(2, 30, int(1e06))
    
    return toy



signal0 = np.random.poisson(30, int(1e06))
# signal1 = np.random.noncentral_chisquare(2, 30, int(1e06))
# signal2 = np.random.noncentral_chisquare(3, 30, int(1e06))
# signal3 = np.random.noncentral_chisquare(4, 30, int(1e06))
# signal4 = np.random.noncentral_chisquare(5, 30, int(1e06))
signal5 = np.random.noncentral_chisquare(6, 30, int(1e06))
signal6 = np.random.noncentral_chisquare(6, 30, int(1e06))*4
signal61 = np.random.noncentral_chisquare(6, 30, int(1e06))*10
signal62 = np.random.noncentral_chisquare(6, 30, int(1e06))*20
signal7 = np.random.noncentral_chisquare(6, 30, int(1e06)) + 100

# plt.hist(signal0, 200)
# plt.hist(signal1, 200)
# plt.hist(signal2, 200)
# plt.hist(signal3, 200)
# plt.hist(signal4, 200)
plt.hist(signal5, 200, histtype = 'step', label = 'signal 5')
plt.hist(signal6, 200, histtype = 'step', label = 'signal 6')
plt.hist(signal61, 200, histtype = 'step', label = 'signal 61')
plt.hist(signal62, 200, histtype = 'step', label = 'signal 62')
plt.hist(signal7, 200, histtype = 'step', label = 'signal 7')

plt.legend()
plt.show()
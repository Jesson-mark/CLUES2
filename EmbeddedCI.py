from matplotlib import pyplot as plt
import matplotlib.cm as cmm

import numpy as np
import argparse
import matplotlib.patches as mpatches

parser = argparse.ArgumentParser()
parser.add_argument('--freqs',type=str)
parser.add_argument('--post',type=str)
parser.add_argument('--figure',type=str)
parser.add_argument('--posterior_intervals', default=[0.25, 0.5, 0.75, 0.95, 0.999], type=float, nargs='+',
                    help='The posterior thresholds for which to draw different consensus trees.')
args = parser.parse_args()
ConfidenceIntervals = []
ColorIntensity = []
for i in range(len(args.posterior_intervals)):
    ConfidenceIntervals.append(round(args.posterior_intervals[i],4))
    ColorIntensity.append(1 - float(i)/len(args.posterior_intervals))
ConfidenceIntervals.sort()

freqs =  np.loadtxt(args.freqs, delimiter=",", dtype=float)
logpost = np.loadtxt(args.post, delimiter=",", dtype=float)
epochs = np.linspace(0,logpost.shape[1],logpost.shape[1] + 1)
f,ax = plt.subplots(1,1)
f.set_size_inches(20,10)
EXPPOST = np.exp(logpost) # rows are frequency, columns are time interbals

MATRIXTOPLOT = np.zeros((EXPPOST.shape[0],EXPPOST.shape[1]))

for indexx in range(len(ConfidenceIntervals)):
    for timeinterval in epochs:
        if timeinterval == epochs[len(epochs)-1]: break
        tentativespan = 10000000.0
        currentlow = -1
        currenthigh = -1
        TimeSLICE = EXPPOST[:,int(timeinterval)]
        for lowerfrequencyindex in range(len(freqs)):
            for higherfrequencyindex in range(lowerfrequencyindex + 1, len(freqs)):
                possiblesum = np.sum(TimeSLICE[lowerfrequencyindex:higherfrequencyindex])
                rangeofsum = freqs[higherfrequencyindex] - freqs[lowerfrequencyindex]
                if possiblesum >= ConfidenceIntervals[indexx] and rangeofsum < tentativespan:
                    tentativespan = rangeofsum
                    currentlow = lowerfrequencyindex
                    currenthigh = higherfrequencyindex
                elif rangeofsum > tentativespan:
                    break
        for j in range(MATRIXTOPLOT.shape[0]):
            if j >= currentlow and j <= currenthigh:
                MATRIXTOPLOT[j, int(timeinterval)] = np.max([MATRIXTOPLOT[j, int(timeinterval)], ColorIntensity[indexx]])

plt.pcolormesh(epochs[:-1],freqs, MATRIXTOPLOT)
plt.axis((0,len(epochs[:-1]),0,1.0))
plt.ylabel('Derived allele frequency',fontsize=20)
plt.xlabel('Generations before present',fontsize=20)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

cmap = cmm.get_cmap()
handless = []
for i in range(len(ConfidenceIntervals)):
    handless.append(mpatches.Patch(color=cmap(ColorIntensity[i]), label= str(ConfidenceIntervals[i] * 100) + '% Posterior Interval'))

ax.legend(handles=handless, loc='upper right')

plt.savefig('%s.%s'%(args.figure,'png'),format='png', dpi=800, bbox_inches='tight')

#!/usr/bin/env python2.6


# Reads Sasha result file

# For several files use: 
# 
# for i in `find /users/apopov/BEST-RD -name "result"`;
# do
# python2.6 /bliss/users/leal/Python/InducedRadDam/src/DataAnalysis/plot3.py $i
# done
#


import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as lines 
import matplotlib.mlab as mlab

from matplotlib.ticker import OldScalarFormatter

import numpy as np

import sys
import os.path


# Script starts from here
if len(sys.argv) < 2:
    print 'Usage: ' + sys.argv[0] + '[-t <output image file name>] <result file>'
    sys.exit()
    
outputFilePath = None
if sys.argv[1] == '-t' :
    outputFilePath = sys.argv[2] 
    inputFilesPath = sys.argv[3]
else :
    inputFilesPath = sys.argv[1]
    outputFilePath = inputFilesPath.replace('/','_').replace('.','') 

#matplotlib.rcParams.update({'font.size': 14})

#fig =  plt.figure(figsize=(12,9), dpi=80)
fig =  plt.figure(figsize=(10,10), dpi=80)
#fig.subplots_adjust(bottom=0.2)

#fig =  plt.figure()

if outputFilePath is not None:
    fig.canvas.set_window_title(outputFilePath)
    fig.suptitle(outputFilePath, fontsize=12)


numberOfDataSets = 6
#numberOfDataSets = 5
colormap = plt.cm.gist_ncar
colormap_values = [colormap(i) for i in np.linspace(0, 0.9, numberOfDataSets)]
colormap_values_dup = [val for val in colormap_values for _ in (0, 1)]
#plt.gca().set_color_cycle(colormap_values_dup)

# MArkers
#markers = []
#for m in Line2D.markers:
#    try:
#        if len(m) == 1 and m != ' ':
#            markers.append(m)
#    except TypeError:
#        pass
markers = ['D',
 's',
 '^',
 'd',
 'h',
 '*',
 'o',
 '.',
 'p',
 'H',
 'v',
 '<',
 '>',
 '$\\lambda$',
 '$\\bowtie$',
 '$\\circlearrowleft$',
 '$\\clubsuit$',
 '$\\checkmark$']
#markers.sort() 
N = len(markers) 



matplotlib.rc('text', usetex=True)
#matplotlib.rc('font', family='serif')
#matplotlib.rc('font', weight='bold')
matplotlib.rcParams['text.latex.preamble']=[r'\usepackage{amssymb,amsmath}']

    
print 'Parsing file: ',inputFilesPath

inputFile = open(inputFilesPath, "r").readlines()

# tables
bfactorDose = []
scaleDose = []
relIntensityDoseTheory = []
relIntensityDoseExp = []
relIntensityDoseTheoryFitToI = []
relIntensityDoseExpFitToI = []

iterator = inputFile.__iter__()
while True:
    try:
        line = iterator.next()
        
        if line.find('Bfactor vs. Dose (Theory)') >= 0 :
            print line
            iterator.next() # jump line
            while True:
                line = iterator.next()
                if len(line.strip().rstrip().lstrip()) > 0 : 
                    try:
                        bfactorDose.append(map(float,line.split()))
                    except ValueError:
                        #print bfactorDose
                        break

        
        if line.find('Relative Scale vs. Dose') >= 0 :
            print line
            iterator.next() # jump line
            iterator.next() # jump line
            while True:
                line = iterator.next()
                if len(line.strip().rstrip().lstrip()) > 0 :
                    try:
                        scaleDose.append(map(float,line.split()))
                    except ValueError:
                        #print scaleDose
                        break
            
        #if line.find('Relative Intensity total vs. Dose') >= 0 :
        if line.strip().rstrip().lstrip() == 'Relative Intensity total vs. Dose' :
        
            print line
            # d=  2.01  2.27  2.69  3.47  6.00
            line = iterator.next()
            d = line.split()[1:]
            #print d
            iterator.next() # jump theory
            while True:
                line = iterator.next()
                if len(line.strip().rstrip().lstrip()) > 0 :
                    try:
                        relIntensityDoseTheory.append(map(float,line.split()))
                    except ValueError:
                        #print relIntensityDoseTheory
                        break
                
            #print line
            
            while True:
                line = iterator.next()
                if len(line.strip().rstrip().lstrip()) > 0 :
                    try:
                        relIntensityDoseExp.append(map(float,line.split()))
                    except ValueError:
                        #print relIntensityDoseExp
                        break
            
        
        if line.strip().rstrip().lstrip() == 'Relative Intensity total vs. Dose -fit to Intensity' :
        
            print line
            # d=  2.01  2.27  2.69  3.47  6.00
            line = iterator.next()
            dFitToI = line.split()[1:]
            #print dFitToI
            iterator.next() # jump theory
            while True:
                line = iterator.next()
                if len(line.strip().rstrip().lstrip()) > 0 :
                    try:
                        relIntensityDoseTheoryFitToI.append(map(float,line.split()))
                    except ValueError:
                        #print relIntensityDoseTheoryFitToI
                        break
                
            #print line
            
            while True:
                line = iterator.next()
                if len(line.strip().rstrip().lstrip()) > 0 :
                    try:
                        relIntensityDoseExpFitToI.append(map(float,line.split()))
                    except ValueError:
                        #print relIntensityDoseExpFitToI
                        break
                
        
    except StopIteration:
        # StopIteration exception is raised after last element
        break
    
            

i=0

marker = markers[i%N]
color = colormap_values[i]


ax1 = fig.add_subplot(221)
plt.gca().set_color_cycle(colormap_values_dup)

bfactorDose[0].append(0) # dummy value has there's no value here
bfactorDoseArr = np.array(bfactorDose)

ax1.set_title('B-factor vs Dose')
ax1.plot(bfactorDoseArr[1:,0],bfactorDoseArr[1:,2],marker=marker,linewidth=0,markerfacecolor=color)
ax1.plot(bfactorDoseArr[:,0],bfactorDoseArr[:,1])
ax1.set_ylabel('B-Factor ($\AA^2$)')
ax1.set_xlabel('Dose (Gy)')
ax1.xaxis.set_major_formatter(OldScalarFormatter())


###################################################################

ax2 = fig.add_subplot(222)
plt.gca().set_color_cycle(colormap_values_dup)

scaleDose[0].append(0) # dummy value has there's no value here
scaleDoseArr = np.array(scaleDose)

ax2.set_title('Relative Scale vs. Dose')
ax2.plot(scaleDoseArr[1:,0],scaleDoseArr[1:,2],marker=marker,linewidth=0,markerfacecolor=color)
ax2.plot(scaleDoseArr[:,0],scaleDoseArr[:,1])
ax2.set_ylabel('Relative Scale')
ax2.set_xlabel('Dose (Gy)')
ax2.xaxis.set_major_formatter(OldScalarFormatter())

###################################################################
ax3 = fig.add_subplot(223)
plt.gca().set_color_cycle(colormap_values_dup)

relIntensityDoseTheoryArr = np.array(relIntensityDoseTheory)
relIntensityDoseExpArr = np.array(relIntensityDoseExp)



ax3.set_title('Relative Intensity total vs. Dose')



for idx,res in enumerate(d):
    ax3.plot(relIntensityDoseTheoryArr[:,0],relIntensityDoseTheoryArr[:,idx+1])
    ax3.plot(relIntensityDoseExpArr[:,0],relIntensityDoseExpArr[:,idx+1],marker=marker,linewidth=0,markerfacecolor=color,label=res)
    marker = markers[idx+1%N]
    color = colormap_values[idx+1]


ax3.set_ylabel('Relative $<I>$')
ax3.set_xlabel('Dose (Gy)')
ax3.xaxis.set_major_formatter(OldScalarFormatter())

ax3.legend(loc='upper right',fancybox=True, shadow=True)
leg = plt.gca().get_legend()
ltext  = leg.get_texts()  # all the text.Text instance in the legend
plt.setp(ltext, fontsize='small')    # the legend text fontsize

###################################################################


i=0

marker = markers[i%N]
color = colormap_values[i]


ax4 = fig.add_subplot(224)
plt.gca().set_color_cycle(colormap_values_dup)

relIntensityDoseTheoryFitToIArr = np.array(relIntensityDoseTheoryFitToI)
relIntensityDoseExpFitToIArr = np.array(relIntensityDoseExpFitToI)



ax4.set_title('Relative Intensity total vs. Dose - fit to Intensity')


for idx,res in enumerate(dFitToI):
    ax4.plot(relIntensityDoseTheoryFitToIArr[:,0],relIntensityDoseTheoryFitToIArr[:,idx+1])
    ax4.plot(relIntensityDoseExpFitToIArr[:,0],relIntensityDoseExpFitToIArr[:,idx+1],marker=marker,linewidth=0,markerfacecolor=color,label=res)
    marker = markers[idx+1%N]
    color = colormap_values[idx+1]

ax4.set_ylabel('Relative $<I>$')
ax4.set_xlabel('Dose (Gy)')
ax4.xaxis.set_major_formatter(OldScalarFormatter())

ax4.legend(loc='upper right',fancybox=True, shadow=True)
    
leg = plt.gca().get_legend()
ltext  = leg.get_texts()  # all the text.Text instance in the legend
plt.setp(ltext, fontsize='small')    # the legend text fontsize

try :
    fig.savefig(outputFilePath+'.png', dpi=(200))
    
except :
    print 'Impossible to save figure: ' + outputFilePath
    print "Unexpected error:", sys.exc_info()[0]

#plt.show()

plt.draw()

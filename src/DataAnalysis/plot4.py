#!/usr/bin/env python2.6

"""
Reads several  Sasha result file
B-factor
Relative Scale
Intensity with theoretical fitting
  Will find the optimal resolution
against dose


Run as:

python2.6 /bliss/users/leal/Python/InducedRadDam/src/DataAnalysis/plot4.py -t test `find . -name "result"`

"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as lines 
import matplotlib.mlab as mlab

from matplotlib.ticker import OldScalarFormatter

import numpy as np

import sys
import os.path


#resolution = 2.5


# Script starts from here
if len(sys.argv) < 2:
    print 'Usage: ' + sys.argv[0] + '[-t <output image file name>] <result file> <result file> (...) <result file> '
    sys.exit()
    
outputFilePath = None
if sys.argv[1] == '-t' :
    outputFilePath = sys.argv[2] 
    inputFilesPath = sys.argv[3:]
else :
    inputFilesPath = sys.argv[1:]


#matplotlib.rcParams.update({'font.size': 14})

#fig =  plt.figure(figsize=(12,9), dpi=80)
fig =  plt.figure(figsize=(10,10), dpi=80)

#fig =  plt.figure()

if outputFilePath is not None:
    fig.canvas.set_window_title(outputFilePath)
    fig.suptitle(outputFilePath, fontsize=12)


numberOfDataSets = len(inputFilesPath)
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

print colormap_values

matplotlib.rc('text', usetex=True)
#matplotlib.rc('font', family='serif')
#matplotlib.rc('font', weight='bold')
matplotlib.rcParams['text.latex.preamble']=[r'\usepackage{amssymb,amsmath}']

for i,inputFilePath in enumerate(inputFilesPath):
    
    print 'Parsing file: ',inputFilePath
    
    inputFile = open(inputFilePath, "r").readlines()
    
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
        
                
    
    marker = markers[i%N]
    color = colormap_values[i]
    
    if i == 0:
        ax1 = fig.add_subplot(221)
        plt.gca().set_color_cycle(colormap_values_dup)
        
    bfactorDose[0].append(0) # dummy value has there's no value here
    bfactorDoseArr = np.array(bfactorDose)
    
    ax1.set_title('B-factor vs Dose')
    ax1.plot(bfactorDoseArr[1:,0],bfactorDoseArr[1:,2],marker=marker,linewidth=0,markerfacecolor=color)
    ax1.plot(bfactorDoseArr[:,0],bfactorDoseArr[:,1])
    ax1.set_ylabel('B-Factor ($\AA^2$)')
    ax1.set_xlabel('Dose (MGy)')
    ax1.xaxis.set_major_formatter(OldScalarFormatter())
    
    
    ###################################################################
    
    if i == 0:
        ax2 = fig.add_subplot(222)
        plt.gca().set_color_cycle(colormap_values_dup)
    
    scaleDose[0].append(0) # dummy value has there's no value here
    scaleDoseArr = np.array(scaleDose)
    
    ax2.set_title('Relative Scale vs. Dose')
    ax2.plot(scaleDoseArr[1:,0],scaleDoseArr[1:,2],marker=marker,linewidth=0,markerfacecolor=color)
    ax2.plot(scaleDoseArr[:,0],scaleDoseArr[:,1])
    ax2.set_ylabel('Relative Scale')
    ax2.set_xlabel('Dose (MGy)')
    ax2.xaxis.set_major_formatter(OldScalarFormatter())
    
    ###################################################################
    if i == 0:
        ax3 = fig.add_subplot(223)
        plt.gca().set_color_cycle(colormap_values_dup)
    
    relIntensityDoseTheoryArr = np.array(relIntensityDoseTheory)
    relIntensityDoseExpArr = np.array(relIntensityDoseExp)
    
    
    
    ax3.set_title('Relative Intensity total vs. Dose')
    
    
    
    ax3.plot(relIntensityDoseTheoryArr[:,0],relIntensityDoseTheoryArr[:,1])
    ax3.plot(relIntensityDoseExpArr[:,0],relIntensityDoseExpArr[:,1],marker=marker,linewidth=0,markerfacecolor=color,label=os.path.basename(os.path.dirname(inputFilePath)))

    
    ax3.set_ylabel('Relative $<I>$')
    ax3.set_xlabel('Dose (MGy)')
    ax3.xaxis.set_major_formatter(OldScalarFormatter())

matplotlib.rc('text', usetex=False)
    
#ax3.legend(loc='upper right',fancybox=True, shadow=True)
#leg = plt.gca().get_legend()
#ltext  = leg.get_texts()  # all the text.Text instance in the legend
#plt.setp(ltext, fontsize='small')    # the legend text fontsize

# Shink current axis
box = ax3.get_position()

#ax3.set_position([box.x0, box.y0, box.width * 0.98, box.height])
# Put a legend to the right of the current axis
#ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#ax3.legend(loc='center left', bbox_to_anchor=(0.92, 0.8))

# Put a legend below current axis
ax3.legend(loc='upper center', bbox_to_anchor=(1.4, 1.05),
fancybox=True, shadow=True, ncol=1)


if outputFilePath is not None: 
    try :
        fig.savefig(outputFilePath+'.png', dpi=(200))
        plt.draw()
    except :
        print 'Impossible to save figure: ' + outputFilePath
        print "Unexpected error:", sys.exc_info()[0]
    
else:
    plt.show()


#!/usr/bin/env python2.6


# Reads several csv files and plot:
# B-factor
# Relative Scale
# Intensity with theoretical fitting
# against dose
#
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as lines 
import matplotlib.mlab as mlab

from matplotlib.ticker import OldScalarFormatter

import numpy as np

import sys
import os.path

import tabular as tb

cmd_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cmd_folder,'../'))

import fitting

#resolution = 2.5


# Script starts from here
if len(sys.argv) < 2:
    print 'Usage: ' + sys.argv[0] + ' <csv file> <csv file> (...) <csv file> '
    sys.exit()

# Need this to initialise!
import ini
configIniFileName = '../config.ini'
ini.Ini(configIniFileName)
    
outputFilePath = None
if sys.argv[1] == '-t' :
    outputFilePath = sys.argv[2] 
    inputFilePath = sys.argv[3:]
else :
    inputFilePath = sys.argv[1:]


#matplotlib.rcParams.update({'font.size': 14})

#fig =  plt.figure(figsize=(12,9), dpi=80)
fig =  plt.figure(figsize=(9,12), dpi=80)
fig.subplots_adjust(bottom=0.2)

#fig =  plt.figure()

if outputFilePath is not None:
    fig.canvas.set_window_title(outputFilePath)
    fig.suptitle(outputFilePath, fontsize=12)


numberOfDataSets = len(inputFilePath)
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

for i,inputFilePath in enumerate(inputFilePath):
    
    print 'Parsing CSV file: ',inputFilePath
    
    csvData = tb.tabarray(SVfile=inputFilePath,delimiter=',')
    
    marker = markers[i%N]
    color = colormap_values[i]
    
    # D1/2,absorbedDoseRate,accumulatedDose,accumulatedExposureTime,action,alpha,averageIntegratedIntensity,baseFolderPath,
    # beta,cell_angle_alpha,cell_angle_beta,cell_angle_gamma,cell_length_a,cell_length_b,cell_length_c,completenessOfData,
    # detector_type,dose,ednaFolderName,exposureTime,flux,iOverSigma,initialBFactor,initial_cell_angle_alpha,
    # initial_cell_angle_beta,initial_cell_angle_gamma,initial_cell_length_a,initial_cell_length_b,initial_cell_length_c,
    # initial_mosaicity,invRelativeScale,mosaicity,numberOfImages,numberOfReflections,numberOfReflectionsObserved,
    # oscillationWidth,overallBFactor,processFolderPath,rMeas,realAbsorbedDoseRate,realAccumulatedDose,realAlpha,realBeta,
    # realD1/2,realDose,realInitialBFactor,realInvRelativeScale,realRelativeAverageIntegratedIntensity,realRelativeOverallBFactor,
    # realRelativeScaleS0,relativeAverageIntegratedIntensity,relativeOverallBFactor,relativeScale,relativeScaleS0,resolution,
    # rotationAxisEnd,rotationAxisStart,solventContent,spaceGroup_ITNumber,spaceGroup_name,strategyResolution,subWedgeNumber,
    # susceptibility,transmission,wavelength,wedgeDatasetNumber,wedgeFolderPath,wedgeName,wedgeSoftware

    if i == 0:
        ax1 = fig.add_subplot(311)
        plt.gca().set_color_cycle(colormap_values_dup)
    
    realAccumulatedDose = csvData['realAccumulatedDose']
    #realRelativeOverallBFactor = csvData[r'realRelativeOverallBFactor']
    realRelativeOverallBFactor = csvData['overallBFactor']
    
    realOverallBFactorFitting = fitting.Fitting(realAccumulatedDose,realRelativeOverallBFactor)
    realOverallBFactorFitting.setContinuousX()
    realOverallBFactorFitting.linearFitting2Coeffs()
    realOverallBFactorFitting.setContinuousY()
    
    beta = csvData['realBeta'][-1]
    
    ax1.plot(realAccumulatedDose,realRelativeOverallBFactor,marker=marker,linewidth=0,markerfacecolor=color,label='$\\beta=%.1e$'%beta)
    ax1.plot(realOverallBFactorFitting.continuous_x,realOverallBFactorFitting.continuous_y)
    
    ax1.set_ylabel('B-Factor ($\AA^2$)')
    ax1.set_xlabel('Dose (Gy)')
    ax1.xaxis.set_major_formatter(OldScalarFormatter())
    
    # Shink current axis
    #box = ax1.get_position()
    #ax1.set_position([box.x0, box.y0, box.width * 0.98, box.height])
    # Put a legend to the right of the current axis
    #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #ax1.legend(loc='center left', bbox_to_anchor=(0.95, 0.8))

    
    ##################################################################
    if i == 0:
        ax2 = fig.add_subplot(312)
        plt.gca().set_color_cycle(colormap_values_dup)

    realInvRelativeScale = csvData['realInvRelativeScale']
    alpha = csvData['realAlpha'][-1]
    
    realInvRelativeScaleFitting = fitting.Fitting(realAccumulatedDose,realInvRelativeScale)
    realInvRelativeScaleFitting.setContinuousX()
    realInvRelativeScaleFitting.coefficients = [alpha]
    realInvRelativeScaleFitting.function = realInvRelativeScaleFitting.funcExponentialSquaredNegative1coeffs
    realInvRelativeScaleFitting.setContinuousY()
    
    ax2.plot(realAccumulatedDose,realInvRelativeScale,marker=marker,linewidth=0,label='$\\alpha=%.1e$'%alpha)
    ax2.plot(realInvRelativeScaleFitting.continuous_x,realInvRelativeScaleFitting.continuous_y)
    
    ax2.set_ylabel('Relative Scale')
    ax2.set_xlabel('Dose (Gy)')
    ax2.xaxis.set_major_formatter(OldScalarFormatter())
    
    # Shink current axis
    #box = ax2.get_position()
    #ax2.set_position([box.x0, box.y0, box.width * 0.98, box.height])
    # Put a legend to the right of the current axis
    #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #ax2.legend(loc='center left', bbox_to_anchor=(0.95, 0.8))
    
    
    ##################################################################
    if i == 0:
        ax3 = fig.add_subplot(313)
        plt.gca().set_color_cycle(colormap_values_dup)
        
    realRelativeAverageIntegratedIntensity = csvData['realRelativeAverageIntegratedIntensity']
    initialB = csvData['realInitialBFactor'][-1]
    
    
    realRelativeAverageIntegratedIntensityFitting = fitting.Fitting(realAccumulatedDose,realRelativeAverageIntegratedIntensity)    
    realRelativeAverageIntegratedIntensityFitting.setContinuousX()
    realRelativeAverageIntegratedIntensityFitting.calculateTheoreticalIntensityDecay(beta = beta,
                                                                         gamma = alpha,
                                                                         initialWilsonB= initialB)
    resolution = csvData['strategyResolution'][-1]
    #resolution +=0.25
    realRelativeAverageIntegratedIntensityFitting.doTheoreticalIntensityDecayCurve(resolution=resolution)
    realDsOneHalf = realRelativeAverageIntegratedIntensityFitting.getTheoreticalDOneHalf()
    print '********************** realD1/2',realDsOneHalf
 
    
    ax3.plot(realAccumulatedDose,realRelativeAverageIntegratedIntensity,marker=marker,linewidth=0,
             label='${\\mathbf D_{1/2}}=%.1e$'%realDsOneHalf + ': ${\\boldsymbol\\alpha}=%.1e$'%alpha + ': ${\\boldsymbol\\beta}=%.1e$'%beta + ': $%.2f{\\mathbf\\AA}$'%resolution)
    ax3.plot(realRelativeAverageIntegratedIntensityFitting.continuous_x,realRelativeAverageIntegratedIntensityFitting.continuous_y)
    
    ax3.set_ylabel('Relative $<I>$')
    ax3.set_xlabel('Dose (Gy)')
    ax3.xaxis.set_major_formatter(OldScalarFormatter())
    # Shink current axis
    box = ax3.get_position()
    
    #ax3.set_position([box.x0, box.y0, box.width * 0.98, box.height])
    # Put a legend to the right of the current axis
    #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #ax3.legend(loc='center left', bbox_to_anchor=(0.92, 0.8))
    
    # Put a legend below current axis
    ax3.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
    fancybox=True, shadow=True, ncol=2)


    
leg = plt.gca().get_legend()
ltext  = leg.get_texts()  # all the text.Text instance in the legend
plt.setp(ltext, fontsize='small')    # the legend text fontsize

fig.savefig(outputFilePath+'.png', dpi=(200))
#plt.show()
plt.draw()

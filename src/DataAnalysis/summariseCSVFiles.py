#!/usr/bin/env python2.6

'''
Created on Jul 29, 2011

@author: leal
'''

# Run as:
#
# /segfs/bliss/bin/python2.6  exec `find . -name "xds_t*csv"`
#

import os
import os.path
import sys
import time
import numpy as np
import matplotlib.mlab as mlab

cmd_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cmd_folder,'../'))
import tabular as tb
        
outputFileName = 'summary.csv'
headers = ['Path','EdnaFolderName','WedgeName','SpaceGroup','a','b','c','alpha','beta','gamma','SolventContent','Energy',
           'StrategyResolution','Resolution','Flux','DoseRate','TotalDose','InitialBFactor','Beta','Alpha','D1/2','InitialMosaicity',
           'FinalMosaicity','InitialIOverSigma','FinalIOverSigma','NumOfWedgesUsed']

if len(sys.argv) < 2:
    print 'Usage: ' + sys.argv[0] + ' <csv file> <csv file> (...) <csv file> '
    sys.exit()
    
csvFileList = sys.argv[1:]
recordList = []
for csvFile in csvFileList:
    print 'Checking CSV file: ', csvFile
    csvData = tb.tabarray(SVfile=csvFile,delimiter=',')
    
    record = []
    record.append(csvData['processFolderPath'][-1])
    record.append(csvData['ednaFolderName'][-1])
    record.append(csvData['wedgeName'][-1])
    record.append(csvData['spaceGroup_name'][-1])
    record.append(csvData['initial_cell_length_a'][-1])
    record.append(csvData['initial_cell_length_b'][-1])
    record.append(csvData['initial_cell_length_c'][-1])
    record.append(csvData['initial_cell_angle_alpha'][-1])
    record.append(csvData['initial_cell_angle_beta'][-1])
    record.append(csvData['initial_cell_angle_gamma'][-1])
    record.append(csvData['solventContent'][-1])
    #     E=h\nu=\frac{hc}{\lambda}=\frac{(4.135 667 33\times 10^{-15}\,\mbox{eV}\,\mbox{s})(299\,792\,458\,\mbox{m/s})}{\lambda} 
    energy = 4.13566733e-15 * 299792458 / (csvData['wavelength'][-1]*1e-10)
    #record.append(csvData['wavelength'][-1])
    record.append(energy)
    # strategy resolution:
    record.append(csvData['strategyResolution'][-1])
    record.append(csvData['resolution'][-1])
    
    record.append(csvData['flux'][-1])
    record.append(csvData['realAbsorbedDoseRate'][-1])
    record.append(csvData['realAccumulatedDose'][-1])
    record.append(csvData['realInitialBFactor'][-1])
    record.append(csvData['realBeta'][-1])
    record.append(csvData['realAlpha'][-1])
    record.append(csvData['realD1/2'][-1])
    #record.append(csvData['initial_mosaicity'][-1])
    record.append(csvData['mosaicity'][0])
    record.append(csvData['mosaicity'][-1])
    record.append(csvData['iOverSigma'][0])
    record.append(csvData['iOverSigma'][-1])
    record.append(csvData.size)
    recordList.append(record)

content = tb.tabarray(records = recordList, names=headers)

# averages
averages = []
averages.append('Averages')
averages.append(content.size) # Number of measurements
averages.append('')
averages.append('')
averages.append(np.average(content['a']))
averages.append(np.average(content['b']))
averages.append(np.average(content['c']))
averages.append(np.average(content['alpha']))
averages.append(np.average(content['beta']))
averages.append(np.average(content['gamma']))
averages.append(np.average(content['SolventContent']))
averages.append(np.average(content['Energy']))
averages.append(np.average(content['StrategyResolution']))
averages.append(np.average(content['Resolution']))
averages.append(np.average(content['Flux']))
averages.append(np.average(content['DoseRate']))
averages.append(np.average(content['TotalDose']))
averages.append(np.average(content['InitialBFactor']))
averages.append(np.average(content['Beta']))
averages.append(np.average(content['Alpha']))
averages.append(np.average(content['D1/2']))
averages.append(np.average(content['InitialMosaicity']))
averages.append(np.average(content['FinalMosaicity']))
averages.append(np.average(content['InitialIOverSigma']))
averages.append(np.average(content['FinalIOverSigma']))
averages.append(np.average(content['NumOfWedgesUsed']))



# averages
stdDeviations = []
stdDeviations.append('stdDeviations')
stdDeviations.append(content.size) # Number of measurements
stdDeviations.append('')
stdDeviations.append('')
stdDeviations.append(np.std(content['a']))
stdDeviations.append(np.std(content['b']))
stdDeviations.append(np.std(content['c']))
stdDeviations.append(np.std(content['alpha']))
stdDeviations.append(np.std(content['beta']))
stdDeviations.append(np.std(content['gamma']))
stdDeviations.append(np.std(content['SolventContent']))
stdDeviations.append(np.std(content['Energy']))
stdDeviations.append(np.std(content['StrategyResolution']))
stdDeviations.append(np.std(content['Resolution']))
stdDeviations.append(np.std(content['Flux']))
stdDeviations.append(np.std(content['DoseRate']))
stdDeviations.append(np.std(content['TotalDose']))
stdDeviations.append(np.std(content['InitialBFactor']))
stdDeviations.append(np.std(content['Beta']))
stdDeviations.append(np.std(content['Alpha']))
stdDeviations.append(np.std(content['D1/2']))
stdDeviations.append(np.std(content['InitialMosaicity']))
stdDeviations.append(np.std(content['FinalMosaicity']))
stdDeviations.append(np.std(content['InitialIOverSigma']))
stdDeviations.append(np.std(content['FinalIOverSigma']))
stdDeviations.append(np.std(content['NumOfWedgesUsed']))


# Min
minimums = []
minimums.append('minimums')
minimums.append(content.size) # Number of measurements
minimums.append('')
minimums.append('')
minimums.append(np.min(content['a']))
minimums.append(np.min(content['b']))
minimums.append(np.min(content['c']))
minimums.append(np.min(content['alpha']))
minimums.append(np.min(content['beta']))
minimums.append(np.min(content['gamma']))
minimums.append(np.min(content['SolventContent']))
minimums.append(np.min(content['Energy']))
minimums.append(np.min(content['StrategyResolution']))
minimums.append(np.min(content['Resolution']))
minimums.append(np.min(content['Flux']))
minimums.append(np.min(content['DoseRate']))
minimums.append(np.min(content['TotalDose']))
minimums.append(np.min(content['InitialBFactor']))
minimums.append(np.min(content['Beta']))
minimums.append(np.min(content['Alpha']))
minimums.append(np.min(content['D1/2']))
minimums.append(np.min(content['InitialMosaicity']))
minimums.append(np.min(content['FinalMosaicity']))
minimums.append(np.min(content['InitialIOverSigma']))
minimums.append(np.min(content['FinalIOverSigma']))
minimums.append(np.min(content['NumOfWedgesUsed']))


# Max
maximums = []
maximums.append('maximums')
maximums.append(content.size) # Number of measurements
maximums.append('')
maximums.append('')
maximums.append(np.max(content['a']))
maximums.append(np.max(content['b']))
maximums.append(np.max(content['c']))
maximums.append(np.max(content['alpha']))
maximums.append(np.max(content['beta']))
maximums.append(np.max(content['gamma']))
maximums.append(np.max(content['SolventContent']))
maximums.append(np.max(content['Energy']))
maximums.append(np.max(content['StrategyResolution']))
maximums.append(np.max(content['Resolution']))
maximums.append(np.max(content['Flux']))
maximums.append(np.max(content['DoseRate']))
maximums.append(np.max(content['TotalDose']))
maximums.append(np.max(content['InitialBFactor']))
maximums.append(np.max(content['Beta']))
maximums.append(np.max(content['Alpha']))
maximums.append(np.max(content['D1/2']))
maximums.append(np.max(content['InitialMosaicity']))
maximums.append(np.max(content['FinalMosaicity']))
maximums.append(np.max(content['InitialIOverSigma']))
maximums.append(np.max(content['FinalIOverSigma']))
maximums.append(np.max(content['NumOfWedgesUsed']))

#print len(content.dtype)
#print len(headers)
#print len(averages)
#print len(stdDeviations)
#print headers
#print content.dtype.names

content = content.addrecords(tuple(averages))
content = content.addrecords(tuple(stdDeviations))
content = content.addrecords(tuple(minimums))
content = content.addrecords(tuple(maximums))

#if not os.path.exists(outputFileName) or os.stat(outputFileName)[6]==0 : # file empty

content.saveSV(outputFileName,delimiter=',')   


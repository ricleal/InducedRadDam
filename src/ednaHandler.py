import localLogger
import sys
sys.path.append("/opt/pxsoft/EDNA/vdefault/edna/mxv1/src")
sys.path.append("/opt/pxsoft/EDNA/vdefault/edna/kernel/src")
sys.path.append("/opt/pxsoft/EDNA/vdefault/edna/mxv1/plugins/EDPluginControlInterfaceToMXCuBE-v1.3/plugins")

import XSDataMXv1 
import XSDataMXCuBEv1_3

import numpy as np
import pprint as pp
"""

export PYTHONPATH=/opt/pxsoft/EDNA/vdefault/edna/mxv1/plugins/EDPluginControlInterfaceToMXCuBE-v1.3/plugins:/opt/pxsoft/EDNA/vdefault/edna/kernel/src:/opt/pxsoft/EDNA/vdefault/edna/mxv1/src


"""


class EdnaHandler():
    """
    conventions:
    
    xxFolderName
    xxFolderPath
    xxFileName
    xxFilePath
    
    """

    def __init__(self,ednaOutputFile):
        """
        Parse
        
        ControlInterfaceToMXCuBEv1_3_dataOutput.xml
        
        """
        
        self.ednaOutputFile = ednaOutputFile
        self.log = localLogger.LocalLogger("edna")
        self.log.logger.debug("Parsing edna Output File file: " + self.ednaOutputFile)
        
        # Workaround to process old EDNA characterisation XML format
        # ControlInterfaceToMXCuBEv1_2/CCP4i/Characterisation/ControlCharacterisationv1_2_dataOutput.xml
        if self.ednaOutputFile.find('ControlCharacterisationv1_2') > 0 :
            self._outputXMLContent = XSDataMXv1.XSDataCharacterisation.parseString(open(self.ednaOutputFile,"rb").read())
        # Workaround to read file sent by Sandor
        elif self.ednaOutputFile.find('mxv1StrategyResult') > 0 :
            self._outputXMLContent = XSDataMXv1.XSDataResultStrategy.parseString(open(self.ednaOutputFile,"rb").read())
        else :
            self._outputXMLContent = XSDataMXCuBEv1_3.XSDataResultMXCuBE.parseString(open(self.ednaOutputFile,"rb").read())
        # variables
        self.subWedgesList = [] # list of dictionaries for parsed subwedges
    
    def parseFile(self):
        """
        Parse the XML file
        """
        if self.ednaOutputFile.find('ControlCharacterisationv1_2') > 0 :
            # ControlCharacterisationv1_2
            strategy = self._outputXMLContent.getStrategyResult().getCollectionPlan()[0].getCollectionStrategy()
            strategySummary = self._outputXMLContent.getStrategyResult().getCollectionPlan()[0].getStrategySummary()
        elif self.ednaOutputFile.find('mxv1StrategyResult') > 0 :
            # for Sandor
            strategy = self._outputXMLContent.getCollectionPlan()[0].getCollectionStrategy()
            strategySummary = self._outputXMLContent.getCollectionPlan()[0].getStrategySummary()
        else :
            strategy = self._outputXMLContent.getCharacterisationResult().getStrategyResult().getCollectionPlan()[0].getCollectionStrategy()
            strategySummary = self._outputXMLContent.getCharacterisationResult().getStrategyResult().getCollectionPlan()[0].getStrategySummary()
            
                
        
        # wedges must be parsed before
        subWedgeList = strategy.getSubWedge()
        self._parseSubWeges(subWedgeList)
        
        sample = strategy.getSample()
        self._parseSample(sample,strategySummary)
        
        
        
        
        
    def _parseSubWeges(self,subWedgeList):
        """
        Parses subweges XML tag
        """
        
        
        for wedge in subWedgeList :
            record = {}
            record['subWedgeNumber'] =  wedge.subWedgeNumber.value
            record['action']= str(wedge.action.value)
            record['exposureTime']= wedge.experimentalCondition.beam.exposureTime.value
            record['flux']= wedge.experimentalCondition.beam.flux.value
            record['transmission']= wedge.experimentalCondition.beam.transmission.value
            record['wavelength']= wedge.experimentalCondition.beam.wavelength.value
            record['oscillationWidth']= wedge.experimentalCondition.goniostat.oscillationWidth.value
            record['rotationAxisStart']= wedge.experimentalCondition.goniostat.rotationAxisStart.value
            record['rotationAxisEnd']= wedge.experimentalCondition.goniostat.rotationAxisEnd.value
            record['detector_type']= str(wedge.experimentalCondition.detector.type.value)
            self.subWedgesList.append(record)
        
        
    
#    def _parseSubWeges(self,subWedgeList):
#        names = ['subWedgeNumber','action','exposureTime','flux','transmission','wavelength',
#                 'oscillationWidth','rotationAxisStart','rotationAxisEnd','detector']
#        record = []
#        records = []
#        
#        for idx,wedge in enumerate(subWedgeList) :
#            record.append( wedge.subWedgeNumber.value)
#            record.append( str(wedge.action.value))
#            record.append( wedge.experimentalCondition.beam.exposureTime.value)
#            record.append( wedge.experimentalCondition.beam.flux.value)
#            record.append( wedge.experimentalCondition.beam.transmission.value)
#            record.append( wedge.experimentalCondition.beam.wavelength.value)
#            record.append( wedge.experimentalCondition.goniostat.oscillationWidth.value)
#            record.append( wedge.experimentalCondition.goniostat.rotationAxisStart.value)
#            record.append( wedge.experimentalCondition.goniostat.rotationAxisEnd.value)
#            record.append( str(wedge.experimentalCondition.detector.type.value))
#            records.append(tuple(record))
#            record = []
#        self.subWedgesList = tb.tabarray(records = records, names=names)
#        print self.subWedgesList
#        print self.subWedgesList.dtype
                
        
    
    def _parseSample(self, sample,summary):
        
        for wedge in self.subWedgesList :
            wedge['absorbedDoseRate']= sample.absorbedDoseRate.value
            wedge['initial_mosaicity']= sample.crystal.mosaicity.value
            try :
                wedge['susceptibility']= sample.susceptibility.value            
            except :
                pass
            wedge['initial_cell_angle_alpha']= sample.crystal.cell.angle_alpha.value
            wedge['initial_cell_angle_beta']= sample.crystal.cell.angle_beta.value
            wedge['initial_cell_angle_gamma']= sample.crystal.cell.angle_gamma.value
            wedge['initial_cell_length_a']= sample.crystal.cell.length_a.value
            wedge['initial_cell_length_b']= sample.crystal.cell.length_b.value
            wedge['initial_cell_length_c']= sample.crystal.cell.length_c.value
            wedge['spaceGroup_name']= str(sample.crystal.spaceGroup.name.value)
            try :
                wedge['spaceGroup_ITNumber']= sample.crystal.spaceGroup.ITNumber.value
            except AttributeError: 
                self.log.logger.info('This sample has no spaceGroup ITNumber!')
            wedge['strategyResolution'] = summary.resolution.value

    
    
#    def _parseSample(self, sample):
#        
#        names = ['absorbedDoseRate','mosaicity','susceptibility','angle_alpha','angle_beta','angle_gamma',
#                 'length_a','length_b','length_c','spaceGroup_name','spaceGroup_ITNumber']
#        record = []
#        record.append( sample.absorbedDoseRate.value)
#        record.append( sample.crystal.mosaicity.value)
#        record.append( sample.susceptibility.value)
#        record.append( sample.crystal.cell.angle_alpha.value)
#        record.append( sample.crystal.cell.angle_beta.value)
#        record.append( sample.crystal.cell.angle_gamma.value)
#        record.append( sample.crystal.cell.length_a.value)
#        record.append( sample.crystal.cell.length_b.value)
#        record.append( sample.crystal.cell.length_c.value)
#        record.append( sample.crystal.spaceGroup.name.value)
#        record.append( sample.crystal.spaceGroup.ITNumber.value)
#        
#        self.summary = tb.tabarray(records = [tuple(record)], names=names)
    
    def doCalculations(self,realAbsorbedDoseRate=None):
        
        previousAccumulatedDose = 0
        previousAccumulatedRealDose = 0
        previousAccumulatedExposureTime = 0
        
        
        self.log.logger.debug("Doing final calculations" + \
                             {True: " using a real Dose Rate of %.2e"%realAbsorbedDoseRate, False: "."}[realAbsorbedDoseRate is not None]  )

        for idx,wedge in enumerate(self.subWedgesList):             # Iterates through all found subWedges             
            if wedge['rotationAxisEnd'] == wedge['rotationAxisStart'] :
                # for burn wedge this is true 
                wedge['numberOfImages'] = 1
            else :
                wedge['numberOfImages'] =  abs( (wedge['rotationAxisEnd'] - wedge['rotationAxisStart']) / wedge['oscillationWidth'] )
                       
            
            # Normally burn cycles use 100% transmission. If they don't use, 
            # the transmission used for collecting is function of the burning transmission
            
            if wedge['action'] == "exposure" :
                if idx < len(self.subWedgesList) - 1 :
                    burningTransmission = self.subWedgesList[idx+1]['transmission']
                else :
                    burningTransmission = self.subWedgesList[idx-1]['transmission']
            else :
                burningTransmission = wedge['transmission']
                        
            wedge['dose'] =  wedge['numberOfImages']  * wedge['exposureTime'] * (wedge['transmission'] / burningTransmission) *  wedge['absorbedDoseRate']
                
            wedge['accumulatedDose'] = previousAccumulatedDose + wedge['dose']
            
            wedge['accumulatedExposureTime'] =  previousAccumulatedExposureTime + wedge['exposureTime'] * wedge['numberOfImages']  * wedge['transmission'] / burningTransmission
            
            if realAbsorbedDoseRate is not None :
                wedge['realAbsorbedDoseRate'] = realAbsorbedDoseRate
                wedge['realDose'] =  wedge['numberOfImages']  * wedge['exposureTime'] * (wedge['transmission'] / burningTransmission) *  realAbsorbedDoseRate                       
                wedge['realAccumulatedDose'] = previousAccumulatedRealDose + wedge['realDose']
                previousAccumulatedRealDose = wedge['realAccumulatedDose']
                
            previousAccumulatedDose = wedge['accumulatedDose']
            previousAccumulatedExposureTime = wedge['accumulatedExposureTime']
            
#        self.log.logger.debug('EDNA subWedgesList:\n%s'%pp.pformat(self.subWedgesList, indent=2,  depth=3))
            

#    def doCalculations(self,realAbsorbedDoseRate=None):
#        names = ['numberOfImages','dose','accumulatedDose','accumulatedExposureTime',
#                 'realDose','realAccumulatedDose']
#        records = []
#        record = []
#        
#        previousAccumulatedDose = 0
#        previousAccumulatedRealDose = 0
#        previousAccumulatedExposureTime = 0
#        
#        for i in range(len(self.subWedgesList)) :
#            
#            # numberOfImages
#            if self.subWedgesList['rotationAxisEnd'][i] == self.subWedgesList['rotationAxisStart'][i]:
#                record.append(1) # burn cycle (oscilation = 1 degree for example!)
#            else :
#                record.append( abs( (self.subWedgesList['rotationAxisEnd'][i] - self.subWedgesList['rotationAxisStart'][i]) 
#                                   / self.subWedgesList['oscillationWidth'][i] ))
#            
#            if self.subWedgesList['action'][i] == "exposure" :
#                if i < len(self.subWedgesList) - 1 :
#                    burningTransmission = self.subWedgesList['transmission'][i+1]
#                else :
#                    burningTransmission = self.subWedgesList['transmission'][i-1]
#            else :
#                burningTransmission = self.subWedgesList['transmission'][i]
#            
#            #Dose
#            record.append( record[-1]  *  self.subWedgesList['exposureTime'][i]
#                            * (self.subWedgesList['transmission'][i]/ burningTransmission) *  self.summary['absorbedDoseRate'][0])
#            #accumulatedDose
#            record.append( previousAccumulatedDose + record[-1] ) # Dose just added
#            # accumulatedExposureTime
#            record.append( previousAccumulatedExposureTime + self.subWedgesList['exposureTime'][i] * record[0]  * 
#                           self.subWedgesList['transmission'][i] / burningTransmission)
#            
#            
#            if realAbsorbedDoseRate is not None :
#                # realDose
#                record.append( self.subWedgesList['numberOfImages'][i]  * self.subWedgesList['exposureTime'][i] * 
#                               (self.subWedgesList['transmission'][i] / burningTransmission) *  realAbsorbedDoseRate)                       
#                # realAccumulatedDose
#                record.append( previousAccumulatedRealDose + self.subWedgesList['realDose'][i])
#                
#                previousAccumulatedRealDose = record[-1]
#                
#            previousAccumulatedDose = record[2] #accumulatedDose
#            previousAccumulatedExposureTime = record[3] #accumulatedExposureTime
#            records.append(tuple(record))
#            record = []
#        table = tb.tabarray(records = records, names=names)
#        self.subWedgesList = self.subWedgesList.colstack(table)
#        print self.subWedgesList
#        print self.subWedgesList.dtype
#        self.subWedgesList.saveSV('/tmp/test.csv',delimiter=',')
    
    
    def getCellAsString(self):
        return "%.2f %.2f %.2f %.2f %.2f %.2f " %(self.subWedgesList[0]['initial_cell_length_a'],
                                                  self.subWedgesList[0]['initial_cell_length_b'],
                                                  self.subWedgesList[0]['initial_cell_length_c'],
                                                  self.subWedgesList[0]['initial_cell_angle_alpha'],
                                                  self.subWedgesList[0]['initial_cell_angle_beta'],
                                                  self.subWedgesList[0]['initial_cell_angle_gamma'])
    def getSpaceGroupNumber(self):
        return self.subWedgesList[0]['spaceGroup_ITNumber']
    
    def getDetectorType(self):
        return self.subWedgesList[0]['detector_type']
    
    def getExposureTime(self):
        return self.subWedgesList[0]['exposureTime']


if __name__ == '__main__':
    
    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)
    
    # same file!
    #e = EdnaHandler('/data/id23eh1/inhouse/opid231/20110515/PROCESSED_DATA/APERT_INS/EDNAOutput_886842.xml')
    e = EdnaHandler('/data/id23eh1/inhouse/opid231/20110515/PROCESSED_DATA/APERT_INS/EDApplication_20110515-191124/ControlInterfaceToMXCuBEv1_3/ControlInterfaceToMXCuBEv1_3_dataOutput.xml')
    e.parseFile()
    e.doCalculations()
    e.doCalculations(realAbsorbedDoseRate=60e3,)
    
    pp.pprint(e.subWedgesList)
    
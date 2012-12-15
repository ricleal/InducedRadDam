'''
Created on May 20, 2011

@author: leal
'''

import localLogger
import sys
import os
import re
import pprint

class WedgeHandler():
    '''
    
    This  only handles the wedge folder name!
    
    conventions:
    
    xxFolderName
    xxFolderPath
    xxFileName
    xxFilePath
    
    
    
    '''


    def __init__(self, wedgeFolderPath):
        '''
        Constructor
        
        Two types of wedgeFolderPath
    
        # old : /data/id23eh1/inhouse/opid231/20100930/HUM/Ricardo/Lyso1/process/xds_t4w1_run1_1
        # new : /data/id23eh1/inhouse/opid231/20101103/PROCESSED_DATA/LYS_T/xds_t3w7_run1_1
    
        '''
        
        self.log = localLogger.LocalLogger("wedge")
        
        
        # normalize path (just for safety...)
        if os.path.isabs(wedgeFolderPath) and os.path.exists(wedgeFolderPath) :
            self.wedgeFolderPath = os.path.normpath(wedgeFolderPath)
        # if is relative path, build complete path
        elif not os.path.isabs(wedgeFolderPath) and os.path.exists(os.path.abspath(wedgeFolderPath)) :
            self.wedgeFolderPath = os.path.abspath(wedgeFolderPath)
        else :
            self.log.logger.error("Wedge folder does not exist: " + wedgeFolderPath )
            sys.exit(-1)
        
        self.log.logger.debug("Parsing: " + self.wedgeFolderPath )
        
        # 
        self.baseFolderPath = None
        self.processFolderPath = None
        self._getBaseFolderPath()
        #
        self.wedgeFolderName = None
        self.wedgeSoftware = None
        self.wedgeName = None
        self.subWedgeNumber = None
        self.wedgeRunNumber = None
        self.wedgeDatasetNumber = None
        self._parseCurrentWedgeNumber()
        
    #===========================================================================
    # Private methods
    #===========================================================================        
    
    def _getBaseFolderPath(self):
        '''
        From the wedge folder path gets the root folder
        
        # old : /data/id23eh1/inhouse/opid231/20100930/HUM/Ricardo/Lyso1/process/xds_t4w1_run1_1
        # new : /data/id23eh1/inhouse/opid231/20101103/PROCESSED_DATA/LYS_T/xds_t3w7_run1_1
        
        self.baseFolderPath = /data/id23eh1/inhouse/opid231/20100930/HUM/Ricardo/Lyso1
        self.processFolderPath = /data/id23eh1/inhouse/opid231/20100930/HUM/Ricardo/Lyso1/process
        
        self.baseFolderPath = /data/id23eh1/inhouse/opid231/20101103/PROCESSED_DATA/LYS_T
        self.processFolderPath = /data/id23eh1/inhouse/opid231/20101103/PROCESSED_DATA/LYS_T


        '''
        if self.wedgeFolderPath.split(os.sep)[-2] == 'process' :
            self.baseFolderPath = os.sep.join(self.wedgeFolderPath.split(os.sep)[:-2])
            self.processFolderPath = os.sep.join(self.wedgeFolderPath.split(os.sep)[:-1])
        else :
            self.baseFolderPath = os.sep.join(self.wedgeFolderPath.split(os.sep)[:-1])
            self.processFolderPath = self.baseFolderPath
                
        self.log.logger.debug("baseFolderPath: " + self.baseFolderPath )
        self.log.logger.debug("processFolderPath: " + self.processFolderPath )
        
        
    def _parseCurrentWedgeNumber(self):
        """
        Get the current wedge from the XDS path:    
        /data/id23eh1/inhouse/opid231/20100716/Trypsin1/process/xds_t2w21_run1_1
        """
        
        self.wedgeFolderName = os.path.basename(self.wedgeFolderPath)
        
        # usually pattern are of form xds_<wedgeName>w<n>_run<n>_<n>     xds_A2-24963w11_run1_1   
        wedgePattern   = re.compile('([a-zA-Z]+)_([a-zA-Z0-9_\-]+)w(\d+)_run(\d+)_(\d+)$')
        wedgeData = wedgePattern.search(self.wedgeFolderName )
        
        if wedgeData is not None :
            # this folder matches the pattern
            wedgeData = wedgeData.groups()
            self.wedgeSoftware = wedgeData[0]
            self.wedgeName = wedgeData[1]
            self.subWedgeNumber = int(wedgeData[2]) # wedge_number
            self.wedgeRunNumber = int(wedgeData[3])
            self.wedgeDatasetNumber = int(wedgeData[4])
        else :
            # usually pattern are of form xds_<wedgeName>_run<n>_<n>        
            wedgePattern   = re.compile('([a-zA-Z]+)_([a-zA-Z0-9_\-]+)_run(\d+)_(\d+)$')
            wedgeData = wedgePattern.search(self.wedgeFolderName )
            if wedgeData is not None :
                # this folder matches the pattern
                
                wedgeData = wedgeData.groups()
                self.wedgeSoftware = wedgeData[0]
                self.wedgeName = wedgeData[1]
                self.subWedgeNumber = int(wedgeData[2]) # Run here is the wedge subWedgeNumber!
                self.wedgeDatasetNumber = int(wedgeData[3])
                self.wedgeRunNumber = None
           
            else :
                self.log.logger.error("Couldn't get the current wedge subWedgeNumber from the folder: " + self.wedgeFolderName)
                sys.exit(0)
    
    #===========================================================================
    #  Global methods
    #===========================================================================
    def buildEdnaFolderPath(self,ednaFolderName):
        '''
        ednaFolderName
        
        Builds complete path from the folder wedgeName
        
        '''
        self.ednaFolderName = ednaFolderName
        # For Sandor
        # if ednaFolderName is a complete path to an XML file don't build the path
        if os.path.isfile(ednaFolderName):
            self.ednaFolderPath = ednaFolderName
        else:
            self.ednaFolderPath = os.path.join( self.baseFolderPath,ednaFolderName)
        self.log.logger.debug("ednaPath: %s"%self.ednaFolderPath)
    
    
    def getWedgeFolderPath(self,subWedgeNumber) :
        """
        From a wedge number returns the full path for this wedge
        
        """
        
        if self.wedgeRunNumber is None :
            # xds_<wedgeName>_run<n>_<n>
            
            wedgeFolderName =  "%s_%s_run%d_%d" % (self.wedgeSoftware ,self.wedgeName,subWedgeNumber,self.wedgeDatasetNumber)
            self.log.logger.debug("Path of the form: xds_<wedgeName>_run<n>_<n> ")
        else:
            # xds_<wedgeName>w<n>_run<n>_<n> 
            wedgeFolderName = "%s_%sw%d_run%d_%d" %(self.wedgeSoftware, self.wedgeName, subWedgeNumber, self.wedgeRunNumber, self.wedgeDatasetNumber)
            self.log.logger.debug("Path of the form: xds_<wedgeName>w<n>_run<n>_<n> ")
        
        return os.path.join(self.processFolderPath,wedgeFolderName)
        
    def getWedgeFolderName(self,subWedgeNumber) :
        """
        From a wedge number returns the wedge name
        
        """
        
        if self.wedgeRunNumber is None :
            # xds_<wedgeName>_run<n>_<n>
            
            wedgeFolderName =  "%s_%s_run%d_%d" % (self.wedgeSoftware ,self.wedgeName,subWedgeNumber,self.wedgeDatasetNumber)
            self.log.logger.debug("Path of the form: xds_<wedgeName>_run<n>_<n> ")
        else:
            # xds_<wedgeName>w<n>_run<n>_<n> 
            wedgeFolderName = "%s_%sw%d_run%d_%d" %(self.wedgeSoftware, self.wedgeName, subWedgeNumber, self.wedgeRunNumber, self.wedgeDatasetNumber)
            self.log.logger.debug("Path of the form: xds_<wedgeName>w<n>_run<n>_<n> ")
        
        return wedgeFolderName
        
    
    
    
    def putAttributesInADictionary(self):
        """
        
        """
        self.wedgedict = {}
        
        import types as types
        for i in dir(self):
            t = type(getattr(self, i))
            if not i.startswith('_') and t in [types.BooleanType, types.IntType, types.LongType, types.FloatType, types.StringType] :
                #print i, t
                self.wedgedict[i] = getattr(self, i)
        
        
        self.log.logger.debug(pprint.pformat(self.wedgedict, indent=2,  depth=3))
    
    def convertVariablesToDict(self):
        '''
        convert most important variables to a dict
        '''
        self.wedgedict = {}
        self.wedgedict['wedgeFolderPath'] = self.wedgeFolderPath
        self.wedgedict['baseFolderPath'] = self.baseFolderPath
        #self.wedgedict['ednaFolderPath'] = self.ednaFolderPath
        self.wedgedict['ednaFolderName'] = self.ednaFolderName
        self.wedgedict['processFolderPath'] = self.processFolderPath
        self.wedgedict['wedgeDatasetNumber'] = self.wedgeDatasetNumber
        self.wedgedict['wedgeName'] = self.wedgeName
        self.wedgedict['wedgeSoftware'] = self.wedgeSoftware
        
        


        
            
    

if __name__ == '__main__':
    
    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)
    
    
#    print "Old..."
#    wOld = WedgeHandler('/data/id23eh1/inhouse/opid231/20100930/HUM/Ricardo/Lyso1/process/xds_t4w1_run1_1')
#    wOld.buildEdnaFolderPath('EDApplication_20110515-191124')
    print "New..."
    wNew = WedgeHandler('../Data/xds_in1w7_run1_1')
    wNew.buildEdnaFolderPath('EDApplication_20110515-160110')
    print "End..."
    wNew.putAttributesInADictionary()
    
#    print wOld.getWedgeFolderPath(3)    
    print wNew.getWedgeFolderPath(11)
    

    
    
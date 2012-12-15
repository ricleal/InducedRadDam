
import sys
import os
import time
import re
import ini
import localLogger



class XDS :
    """
    Prepares the XDS.INI file 
    """
    
    def __init__(self,xdsRunFolder) :
        self.xdsRunFolder = xdsRunFolder
        self.log = localLogger.LocalLogger("xds")
        self.cell = None
        self.spaceGroupNumber = None
        self.firstImage = None
        self.lastImage = None
        self.referenceDataSet = None
    
    def setCrystal(self,cell,spaceGroupNumber):        
        self.cell = cell
        self.spaceGroupNumber = spaceGroupNumber
    
    def setRange(self,firstImage,lastImage):
        """
        Not needed...
        It gets the image numbers from DATA_RANGE
        """
        self.firstImage = firstImage
        self.lastImage = lastImage
        
    def setReferenceDataSet(self,wedgeFolderName) :
        """
        wedgeFolderPath : wedge.getWedgeFolderPath(ini.Ini().getPar("XDS","xds_reference_data_set_wedge_number"))
        """        
        self.referenceDataSet = os.path.join('..',wedgeFolderName,ini.Ini().getPar("XDS","xds_intensities_file"))
        
        
    def getCellAndSpaceGroup(self):
        """
        Just for sasha
        """
        xdsFile = os.path.join(self.xdsRunFolder,'XDS.INP') 
        inp = open(xdsFile,"r")
        lines = inp.readlines()
        xdsIniEntries = {}
        for line in lines :
            line = line.strip()
            if not line.startswith('!') and len(line) > 1:
                k,v = line.split('=',1) # just for the first =
                xdsIniEntries[k.strip()]=v.strip()
        inp.close()
        return xdsIniEntries['UNIT_CELL_CONSTANTS'],xdsIniEntries['SPACE_GROUP_NUMBER']
 
    
    
    def prepareIniFile(self):
        xdsFile = os.path.join(self.xdsRunFolder,'XDS.INP') 
        
        # wait maxCycles x time.sleep for the file to be in the folder
        maxCycles = 120
        for i in range(0,maxCycles):
            try:
                inp = open(xdsFile,"r")
                break
            except IOError:
                self.log.logger.info("Waiting for the XDS.INP file to be ready... %d of %d" % (i,maxCycles) )
                time.sleep(1);
                if maxCycles == i + 1 :
                    self.log.logger.error("Giving up... Can't open the file: " + xdsFile)
                    sys.exit(3)
                
        
        lines = inp.readlines()
        inp.close()
        # create XDS.INP backup
        xdsBackupFileName = 'XDS.INP_' + str(time.time())
        backupFile = os.path.join(self.xdsRunFolder,xdsBackupFileName)
        outp = open(backupFile,'w')
        outp.writelines(lines)
        outp.close()
        
        self.log.logger.debug("Preparing XDS.INP file. Original file backed up to: " + xdsBackupFileName)
        
        outlines = []
        # Patterns to find
        dataRangePattern   = re.compile('DATA_RANGE\s*=\s*(\d+)\s+(\d+)$')
        # Patterns to substitute        
        spaceGroupNumberPattern   = re.compile('SPACE_GROUP_NUMBER.*$')
        unitCellConstantsPattern = re.compile('UNIT_CELL_CONSTANTS.*$')
        backgroundRangePattern = re.compile('BACKGROUND_RANGE\s*=\s*(\d+)\s+(\d+)$')
        spotRangePattern = re.compile('SPOT_RANGE\s*=\s*(\d+)\s+(\d+)$')
        jobPattern = re.compile('JOB\s*=.*$')
        
        # modify file content
        for line in lines:
            line = line.strip()
            if line.startswith('!') :
                outlines.append(line)
            else :
                dataRange = dataRangePattern.search(line)
                spaceGroupNumber = spaceGroupNumberPattern.search(line)
                unitCellConstants = unitCellConstantsPattern.search(line)
                backgroundRange = backgroundRangePattern.search(line)        
                spotRange = spotRangePattern.search(line)
                job = jobPattern.search(line)
                            
                if dataRange is not None :                
                    self.firstImage = int(dataRange.group(1))
                    self.lastImage = int(dataRange.group(2))
                    self.log.logger.debug("First image = %d, Last image = %d" %(self.firstImage,self.lastImage))
                    outlines.append(line)
                elif spaceGroupNumber is not None and self.spaceGroupNumber is not None:
                    outlines.append(' SPACE_GROUP_NUMBER= ' + str(self.spaceGroupNumber))
                elif unitCellConstants is not None and self.cell is not None:
                    outlines.append(' UNIT_CELL_CONSTANTS= ' + self.cell )
                elif backgroundRange is not None and self.firstImage is not None and self.lastImage is not None:
                    if int(backgroundRange.group(2)) > self.lastImage :
                        outlines.append(' BACKGROUND_RANGE= %d %d \n' % (self.firstImage,self.lastImage))
                    else :
                        outlines.append(line)
                elif spotRange is not None and self.firstImage is not None and self.lastImage is not None:
                    if int(spotRange.group(2)) > self.lastImage :
                        outlines.append(' SPOT_RANGE= %d %d \n' % (self.firstImage,self.lastImage))
                    else :
                        outlines.append(line)
                elif job is not None :
                    outlines.append(' JOB= ' +  ini.Ini().getPar("XDS","xds_job_keywords") + '\n')
                
                elif line.startswith('REFERENCE_DATA_SET') :# and self.referenceDataSet is not None:
                    # cleans previous REFERENCE_DATA_SET
                    pass
                elif line.find('MINUTE=1') >= 0 :
                    # older INP XDS files
                    # doesn't write line to the output
                    pass
                else :
                    outlines.append(line)
        if self.referenceDataSet is not None and self.referenceDataSet.strip() != '' :
            outlines.append('REFERENCE_DATA_SET= ' + self.referenceDataSet)
        
        outp = open(xdsFile,'w')
        #outp.writelines(outlines)
        for l in outlines:
            outp.write(l + '\n')
        outp.close()
        
        
        

if __name__ == "__main__":
    
    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)
    
    xds = XDS('/tmp/ric')
    xds.setCrystal("10 10 10 90 90 90", '12')
    xds.setReferenceDataSet('/tmp/ric/test')
    xds.prepareIniFile()
    
    
    
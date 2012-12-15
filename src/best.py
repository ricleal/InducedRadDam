
import sys
import os
import time
import re
import os.path
import stat
from string import Template

import ini
import localLogger



class Best :
    """
    Prepares the XDS.INI file 
    """
    
    def __init__(self,runFolder) :
        self.runFolder = runFolder
        self.log = localLogger.LocalLogger("best")        
        
    def make_exe(self,fn):
#        if os.name == 'posix':
#            oldmode = os.stat(fn).st_mode & 07777
#            newmode = (oldmode | 0555) & 07777
#            os.chmod(fn, newmode)
#            #print 'Changed mode of %s to %s' % (fn, oct(newmode))
        os.system('chmod +x ' + fn)

    
    def prepareBatchFile(self,detector,exposureTime):
        """
        Prepares a batch file to run Best bfactors only
        It can be used to run in condor as a post script
        
        """
        
        inp = open(ini.Ini().getParTestFile("BEST","best_batch_file_template"), 'r')
        t = Template(inp.read())
        s = t.substitute(besthome=ini.Ini().getPar("BEST","besthome"),
                         bestbin=ini.Ini().getPar("BEST","best_bin"),
                         detector=detector,exposure_time=exposureTime,folder=self.runFolder)
        
        self.completePath = os.path.join(self.runFolder,ini.Ini().getPar("BEST","best_batch_file") )
        outp = open(self.completePath, 'w')
        outp.write(s)
        outp.close()
        # give execute permissions
        #os.chmod(self.completePath, 0755)
        self.make_exe(self.completePath) 
        self.log.logger.debug("Batch best file created: " + self.completePath)
        
        return self.completePath
    

if __name__ == "__main__":
    b = Best('/bliss/users/leal/condor_temp')
    b.prepareBatchFile('315-2x', 0.1)
    
    
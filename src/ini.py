
import sys
import getopt
import os
import re
import time
import os.path
import localLogger
import inspect


from ConfigParser import ConfigParser


class Singleton(type):
    """ 
    
    Singleton!!!
     
    """
    
    def __init__(cls, name, bases, dict):
        
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None
 
    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw) 
        return cls.instance    
    

            
class Ini(object):
    __metaclass__ = Singleton
    
    
    #def __init__(self,iniFile="config.ini"):
    def __init__(self,iniFile):
        
        iniFileRet = self.testIfFileExists(iniFile)
        
        if iniFileRet is None :
            #localLogger.LocalLogger("ini").logger.error("Ini file does not exist: " + iniFile)
            print >> sys.stderr, "Ini file does not exist: %s" % iniFile
            sys.exit(3)
        
        self.cfg = ConfigParser()
        self.cfg.read(iniFileRet)
    
    def testIfFileExists(self,filename):
        """ 
        If file exists in all possible folders,
        return complete file path,
        otherwise, return None
        """
        
        #print "*", filename
        if os.path.isfile(filename) is True :
            #print "*1", filename
            
            return filename
        elif os.path.isfile(os.path.join(os.getcwd(),filename)) is True :
            #print "*2", os.path.isfile(os.path.join(os.getcwd(),filename))
            cfile = os.path.isfile(os.path.join(os.getcwd(),filename))
            
            return cfile
        elif os.path.isfile(os.path.join(os.path.dirname(sys.argv[0]),filename)) is True :
            #print "*3", os.path.join(os.path.dirname(sys.argv[0]),filename)
            cfile =  os.path.join(os.path.dirname(sys.argv[0]),filename)
            
            return cfile        
        elif os.path.isfile(os.path.join(os.path.dirname(inspect.getfile( inspect.currentframe() )),filename)) is True :
            #print "*4", os.path.join(os.path.dirname(inspect.getfile( inspect.currentframe() )),filename)
            cfile = os.path.join(os.path.dirname(inspect.getfile( inspect.currentframe() )),filename)
            
            return cfile
        else :
            #print "*5", filename
            return None
    
    def testIfFileExistsInFolders(self,filename,folderList):
        """ 
        If file exists in all possible folders
        and in the folderList provided
        
        return complete file path,
        otherwise, return None
        """
        
        #print "*", filename
        if os.path.isfile(filename) is True :
            #print "*1", filename
            return filename
        elif os.path.isfile(os.path.join(os.getcwd(),filename)) is True :
            #print "*2", os.path.isfile(os.path.join(os.getcwd(),filename))
            return os.path.isfile(os.path.join(os.getcwd(),filename))
        elif os.path.isfile(os.path.join(os.path.dirname(sys.argv[0]),filename)) is True :
            #print "*3", os.path.join(os.path.dirname(sys.argv[0]),filename)
            return os.path.join(os.path.dirname(sys.argv[0]),filename)        
        elif os.path.isfile(os.path.join(os.path.dirname(inspect.getfile( inspect.currentframe() )),filename)) is True :
            #print "*4", os.path.join(os.path.dirname(inspect.getfile( inspect.currentframe() )),filename)
            return os.path.join(os.path.dirname(inspect.getfile( inspect.currentframe() )),filename)
        else :
            for i in folderList:
                if  os.path.isfile(os.path.join(i,filename)) is True:
                    return os.path.join(i,filename)
            return None
    
    
    def getPar ( self, section, option, default = None ):
        """
        ini.getPar("BEST", "besthome")
        
        """
        if self.cfg.has_section ( section ):
            #print 'Has Section'
            if self.cfg.has_option ( section, option ):
                #print 'Has Option'
                value = self.cfg.get ( section, option ).strip()
            else:
                value = default
        else:
            value = default
        return value
        
    def getParTestFile ( self, section, option, default = None ):
        """
        
        ini.getPar("BEST", "besthome")
        
        Same but tests if file exists and give complete path
        
        """
        if self.cfg.has_section ( section ):
            #print 'Has Section'
            if self.cfg.has_option ( section, option ):
                #print 'Has Option'
                value = self.cfg.get ( section, option ).strip()
            else:
                value = default
        else:
            value = default
        
        
        completeFilePath = self.testIfFileExists(value)
        
        if completeFilePath is None :
            localLogger.LocalLogger("ini").logger.error("Trying tro fetch a file that does not exist: " + value)
            return None
        else :
            return completeFilePath

if __name__ == "__main__":
    print Ini()
    print Ini()
    #print Ini().getParTestFile("BEST","best_cmd")
    print Ini().getPar("BEST","besthome")
    
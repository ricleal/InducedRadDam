#!/usr/bin/env python2.6

"""

Just launches XDS files to the cluster

-p --path <xds path> for the current wedge (the one just collected).
    xds_path is of the form: [/path/path/]xds_<wedge_name>w<wedge_number>_run<run_number>_<dataset_number>

-h --help : show help message
-i --ignore: this will ignore even wedges (e.g. crystal1w2_run1_1) and will process only odd wedges (1,3,5,...,21). Use this when burning wedges are even. Default is True.
-f --first <integer>: first element in the queue (default 1)
-l --last <integer>: of n elements in the queue (default 21)
-u --unset <list of ints>: When showing the results (i.e. processing the last wedge from the queue: current == last), the user may ignore some "dodgy" wedges: e.g. "1,5,7"

Output files:

"""



import sys
import getopt
import os.path
import os
import subprocess as sub
import time
import getpass
import pprint as pp
import datetime
import errno


# local imports
import XDS
import condor
import oar
import best
import localLogger
import ini
import raddose
import wedgeHandler
import ednaHandler
import burntWedgesHandler
import plot
import data
import fitting

__author__ = "Ricardo M. Ferraz Leal"
__copyright__ = "Copyright 2011, European Synchrotron Radiation Facility"
__credits__ = ["Ricardo M. Ferraz Leal", "Alexander N. Popov", "Gleb P. Bourenkov",
                    "Olof Svensson","Darren Spruce","Matias Guijarro"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Ricardo M. Ferraz Leal"
__email__ = "ricardo.leal@esrf.fr"
__status__ = "Production"


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    """
    Main Function
    """
    if argv is None:
        argv = sys.argv
    # Variables
    ignore = True    
    wedgeFolderPath = None
    firstQueueItem = 1
    lastQueueItem = 21 # of
    unsetList = []
    configIniFileName = 'config.ini' 
    
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hie:p:c:l:sr:f:du:t:n:b:", ["help", "ignore", "edna","wedgeFolderPath","current","last","see","raddose","first","draw","unset","resolution","config","bfactor"])
        except getopt.error, msg:
            raise Usage(msg)

        # option processing
        for option, value in opts:
            if option in ("-h", "--help"):
                raise Usage(__doc__)
            elif option in ("-i", "--ignore"):
                ignore = True
            elif option in ("-p", "--wedgeFolderPath"):
                wedgeFolderPath = value
            elif option in ("-l", "--last"):
                lastQueueItem = int(value)
            elif option in ("-f", "--first"):
                firstQueueItem = int(value)
            elif option in ("-u", "--unset"):
                try :
                    unsetListStr = value.split(',')
                    unsetList = [int(i) for i in unsetListStr]
                except :
                    print >> sys.stderr, 'Make sure that the option -u / --unset is followed by a list separated by commas'
                    return 2

                    
         
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, ""
        print >> sys.stderr, "For help use the -h or the --help option."
        print >> sys.stderr, ""
        return 2
    
    
    #===============================================================================
    # Fun starts here!!  
    #===============================================================================
    
    # Mandatory initialisations!
    ini.Ini(configIniFileName)
    myLog = localLogger.LocalLogger()
    #
    
    if wedgeFolderPath is None:
        myLog.logger.info("WedgeFolderPath is mandatory!")
        myLog.logger.info("Type %s -h for help" % sys.argv[0])
        sys.exit(0)
    
    
    # get wedge details from the wedgeFolderPath
    wedge = wedgeHandler.WedgeHandler(wedgeFolderPath)

    myLog.logger.debug("Processing from %d to %d " % (firstQueueItem,lastQueueItem))
    
    # Just an history of what has been done in this folder
    # to delete / move in the future
    f = open(os.path.join(wedge.processFolderPath,'processing_only.log'),'a')
    #f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\t' + wedge.wedgeFolderName + '\t' + ednaFolderName + '\n')
    f.write("%s -> %s\n" %(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") ," ".join(argv)))
    f.close()
    
    
    outFolderPath =  os.path.join(wedge.processFolderPath,wedge.wedgeName)
    myLog.logger.info('Creating folder: %s' % outFolderPath)
    try:
        os.mkdir(outFolderPath)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: 
            print 'Impossible to create folder % for writting output files!'%outFolderPath
            print 'Please create it by hand and relaunch the program!'
    
    
    #TODO
    #Need to put somewherea way to see which wedges failed in the burwedgehandler!!!!
    
    if ignore is True :
        # Only wedge odd numbers are valid
        wedgeRange = range(firstQueueItem,lastQueueItem+1,2)
    else :
        wedgeRange = range(firstQueueItem,lastQueueItem+1)
    
    # remove possible unset wedges:
    if unsetList : # not empty
        wedgeRange = [i for i in wedgeRange if i not in unsetList]
        
    
    for currentQueueItem in wedgeRange :
        currentWedgeFolderName = wedge.getWedgeFolderName(currentQueueItem)
        currentWedgeFolderPath = wedge.getWedgeFolderPath(currentQueueItem)
        
        # Now process folder are generated for burning cycles
        # since there's no image being collected it should not be created
        # This is a workaround.
        if ignore is True and currentQueueItem % 2 == 0 :
            # even wedge
            myLog.logger.debug("Current wedge is even: %d. Ignoring it...", currentQueueItem)   
            if os.path.exists(currentWedgeFolderPath) :
                myLog.logger.debug("Backing up folder: " + currentWedgeFolderPath)
                os.system("mv %s %s_bak" % (currentWedgeFolderPath,currentWedgeFolderPath) )
            sys.exit(0)
        
        myLog.logger.info("Processing wedge %d from %d...",currentQueueItem,lastQueueItem)      
    
    
        #=======================================================================
        # Processing data in parallel
        #=======================================================================    
        # Process data in coral / oar
        
        # Prepare XDS file
        xds = XDS.XDS(currentWedgeFolderPath)
        if currentQueueItem == firstQueueItem :
            cell, spacegroup = xds.getCellAndSpaceGroup()
        xds.setCrystal(cell, spacegroup)
        referenceWedgeNumber = ini.Ini().getPar("XDS","xds_reference_data_set_wedge_number")
        
        if currentQueueItem != firstQueueItem and referenceWedgeNumber is not None:
            xds.setReferenceDataSet(wedge.getWedgeFolderName(int(referenceWedgeNumber)))
            
        xds.prepareIniFile()    
        
        
        if "condor" in ini.Ini().getPar("GENERAL","run_through") : 
            # Prepare Condor files
            print 'Condor not implemented'
            sys.exit(1)
        elif "oar" in ini.Ini().getPar("GENERAL","run_through") :
            myLog.logger.debug("Preparing OAR")
            oarHandler = oar.Oar(currentWedgeFolderPath)
            jobFilePath = oarHandler.createJob(ini.Ini().getPar("XDS","xds_bin"),'echo "Done!"')
            oarHandler.launchJob(jobFilePath)
        else :
            myLog.logger.error("No valid High-Throughput Computing defined in configuration file: " + ini.Ini().getPar("GENERAL","run_through"))
            sys.exit(0)
        
        
        # last element in the queue
        if  currentQueueItem == lastQueueItem :
            # condor_wait returns 1 if unrecoverable errors occur, such as a missing log file, if the job does not exist in the log file, or the user-specified waiting time has expired.
            myLog.logger.info("Condor/OAR waiting for jobs to stop...")
            
            maxCycles = ini.Ini().getPar("GENERAL","number_of_cycles_to_wait_for_processing") 
            for i in range(0,int(maxCycles)):
                # condor entries for current user
                if "condor" in ini.Ini().getPar("GENERAL","run_through") : 
                    command = ini.Ini().getPar("CONDOR","condor_q") + ' | grep ' + getpass.getuser() + ' | egrep \'condor_dagman|xds\''
                elif "oar" in ini.Ini().getPar("GENERAL","run_through") :
                    command = ini.Ini().getPar("OAR","oar_status") + ' -u ' + getpass.getuser() + ' | grep inducedRadDam'
                    
                # execute command and get output
                p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
                output, errors = p.communicate()            
                if errors is not None and len(errors)>0 :
                    myLog.logger.error("Error getting condor/oar Queue: " + command)
                    myLog.logger.error(errors)
                if output is not None and len(output)>0 :
                    myLog.logger.info(command + ':\n'+ output)                
                    myLog.logger.info("Sleeping for 10 seconds: Waiting for the jobs to stop...")
                    time.sleep(10)
                    if maxCycles == i + 1 :
                        myLog.logger.error("I have waited too much for the jobs to finish: Giving up...")
                        sys.exit(2)
                else :
                    myLog.logger.info("Jobs finished")
                    break
        
    #=======================================================================
    # Data Analysis 
    #=======================================================================
    
    myLog.logger.info("Copying files to: %s"%outFolderPath)
    for currentQueueItem in wedgeRange :
        currentWedgeFolderPath = wedge.getWedgeFolderPath(currentQueueItem)
        inHklFile = os.path.join(currentWedgeFolderPath,'XDS_ASCII.HKL')
        outHklFile = os.path.join(outFolderPath,'%d.HKL'%currentQueueItem)
        
        copyCmd = 'cp %s %s' % (inHklFile,outHklFile)
        myLog.logger.debug(copyCmd)
        os.system(copyCmd)
            
      
       
        
    myLog.logger.info("All processing is DONE...")



if __name__ == "__main__":
    
    sys.exit(main()) 

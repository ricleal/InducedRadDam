
import sys
import os
from string import Template
import os.path
import subprocess as sub

import ini
import localLogger

class Oar :
    """
    Creates a condor job and can launch it
    
    oarRunFolder is mandatory!
    
    """
    
    def __init__(self,oarRunFolder) :
        self.oarRunFolder = oarRunFolder
        self.log = localLogger.LocalLogger("oar")
    
    def createJob(self, firstExecutable, secondExecutable ):
        """
        Fills in the template job with the job name and saves it in 
        the oar run folder
        
        firstExecutable : normally XDS
        
        secondExecutable : followed by best
        
        
        return complete job path
        
        """
        inp = open(ini.Ini().getParTestFile("OAR","oar_job_file_template"), 'r')
        t = Template(inp.read())
        
        s = t.substitute(firstExecutable=firstExecutable,secondExecutable=secondExecutable)
        
        completePath = os.path.join(self.oarRunFolder,ini.Ini().getPar("OAR","oar_job_file"))
        outp = open(completePath, 'w')
        outp.write(s)
        outp.close()
        
        os.system('chmod +x ' + completePath)
        
        self.log.logger.debug("OAR Job File created: " + completePath)
        
        return completePath
    
    def launchJob(self, jobFile):
        """ 
        Launches the jobfile
        
        oarsub --stdout='job.%jobid%.out' --stderr='job.%jobid%.err' --name='Run job' -l core=1,walltime=00:03:00 /bliss/users/leal/OAR/job.sh

        """  
        currentFolder =  os.getcwd()
        os.chdir(self.oarRunFolder)
        jobName = os.path.split(self.oarRunFolder)[1]
        
        if os.path.isfile(jobFile) :
            
            command = ini.Ini().getPar("OAR","oar_submit") + '  --stdout=job.oar.out --stderr=job.oar.err --name=inducedRadDam' + ' -l core=1,walltime=' + ini.Ini().getPar("OAR","oar_walltime") + ' ' + jobFile
            
            self.log.logger.debug("Launching job: " + command + " in " + self.oarRunFolder)
            # execute command and get output
            p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
            output, errors = p.communicate()
            if output is not None and len(output)>0 :
                self.log.logger.info(output)
            if errors is not None and len(errors)>0 :
                self.log.logger.error("Error Launching JOB: " + command)
                self.log.logger.error(errors)
            
        else :
            self.log.logger.error( ini.Ini().getPar("OAR","oar_job_file") + " does not exist in " + self.oarRunFolder + ". Have you created the job file?")
        os.chdir(currentFolder)
    

        

if __name__ == "__main__":
    oarHandler = Oar('/tmp_14_days/ric/oar')
    jobFilePath = oarHandler.createJob(ini.Ini().getPar("XDS","xds_bin"),'/tmp_14_days/ric/oar/best.sh')
    oarHandler.launchJob(jobFilePath)
    
    
    
    
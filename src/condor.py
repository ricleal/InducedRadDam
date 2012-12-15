
import sys
import os
from string import Template
import os.path
import subprocess as sub

import ini
import localLogger

class Condor :
    """
    Creates a condor job and can launch it
    
    condorRunFolder is mandatory!
    
    """
    
    def __init__(self,condorRunFolder) :
        self.condorRunFolder = condorRunFolder
        self.log = localLogger.LocalLogger("condor")
    
    def createJob(self, jobFileName,wedgeNumber=0):
        """
        Fills in the template job with the job name and saves it in 
        the condor run folder
        
        jobFileName: executable to be called 
        
        return complete job path
        
        """
        inp = open(ini.Ini().getParTestFile("CONDOR","condor_job_file_template"), 'r')
        t = Template(inp.read())
        executableName = os.path.split(jobFileName)[1]
        
        s = t.substitute(executable=jobFileName,folder=self.condorRunFolder, executable_name=executableName,wedge_number=wedgeNumber)
        
        completePath = os.path.join(self.condorRunFolder,ini.Ini().getPar("CONDOR","condor_job_file"))
        outp = open(completePath, 'w')
        outp.write(s)
        outp.close()
        
        self.log.logger.debug("Job File created: " + completePath)
        
        return completePath
    
    def launchJob(self):
        """ 
        Launches the jobfile  
        """  
        currentFolder =  os.getcwd()
        os.chdir(self.condorRunFolder)
        
        if os.path.isfile(ini.Ini().getPar("CONDOR","condor_job_file")) :
            command = ini.Ini().getPar("CONDOR","condor_submit") + ' ' + ini.Ini().getPar("CONDOR","condor_job_file")
            self.log.logger.debug("Launching job: " + command + " in " + self.condorRunFolder)
            # execute command and get output
            p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
            output, errors = p.communicate()
            if output is not None and len(output)>0 :
                self.log.logger.info(output)
            if errors is not None and len(errors)>0 :
                self.log.logger.error("Error Launching JOB: " + command)
                self.log.logger.error(errors)
            
        else :
            self.log.logger.error( ini.Ini().getPar("CONDOR","condor_job_file") + " does not exist in " + self.condorRunFolder + ". Have you created the job file?")
        os.chdir(currentFolder)
    
    def createDagWithPostScript(self, jobFileName,postScript):
        """
        Fills in the template gag with the job name and the post script 
        and saves it in the condor run folder
        """
        inp = open(ini.Ini().getParTestFile("CONDOR","dag_job_file_template"), 'r')
        t = Template(inp.read())
        s = t.substitute(condor_job_file=jobFileName,post_script_name=postScript)
        
        completePath = os.path.join(self.condorRunFolder,ini.Ini().getPar("CONDOR","dag_job_file"))
        outp = open(completePath, 'w')
        outp.write(s)
        outp.close()
        
        self.log.logger.debug("DAG File created: " + completePath)
    
    def launchDag(self):
        """ 
        Launches the dag file: createDag must be called before
        """  
        currentFolder =  os.getcwd()
        os.chdir(self.condorRunFolder)
        
        if os.path.isfile(ini.Ini().getPar("CONDOR","dag_job_file")) :
            command = ini.Ini().getPar("CONDOR","dag_submit")  + ' ' + ini.Ini().getPar("CONDOR","dag_job_file")
            self.log.logger.debug("Launching dag: " + command + " in " + self.condorRunFolder)            
            # execute command and get output
            p = sub.Popen(command,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
            output, errors = p.communicate()
            if output is not None and len(output)>0 :
                self.log.logger.info(output)
            if errors is not None and len(errors)>0 and errors.find("Renaming rescue DAGs") < 0:
                self.log.logger.error("Error Launching DAG: " + command)
                self.log.logger.error(errors)            
                
        else :
            self.log.logger.error( ini.Ini().getPar("CONDOR","dag_job_file") + " does not exist in " + self.condorRunFolder + ". Have you created the dag file?")
        os.chdir(currentFolder)
        

if __name__ == "__main__":
    c = Condor('/bliss/users/leal/condor_temp')
    jobFilePath = c.createJob('/bliss/users/leal/condor_temp/job.sh')
    #c.launchJob()
    #DAG
    c.createDagWithPostScript(jobFilePath, '/bliss/users/leal/condor_temp/best.sh')
    c.launchDag()
    
    
    
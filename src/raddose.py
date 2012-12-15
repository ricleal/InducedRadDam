
import sys
import os
import time
import subprocess as sub
import localLogger
import ini


class Raddose :
    """
    
    """
    
    def __init__(self,processPath,ednaPath,keysFileName) :
        self._ednaRaddoseExecutable =  os.path.join(ednaPath,ini.Ini().getPar("EDNA","edna_raddose_executable"))        
        self.log = localLogger.LocalLogger("raddose")
        self._keywords = None
        self.results = None
        self.realAbsorbedDoseRate = None
        self.keysFileName = keysFileName
        self.log.logger.debug("Using raddose keywords file: " +  self.keysFileName)
        
    
    def run(self,command) :
        p = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        output, errors = p.communicate()
        if errors is not None and len(errors) > 0 :
            self.log.logger.error(errors)
            return None
        else :
            return output
    
    def make_exe(self,fn):
#        if os.name == 'posix':
#            oldmode = os.stat(fn).st_mode & 07777
#            newmode = (oldmode | 0555) & 07777
#            os.chmod(fn, newmode)
#            #print 'Changed mode of %s to %s' % (fn, oct(newmode))
        try:
            os.system('chmod +x ' + fn)
        except Exception as detail:
            self.log.logger.warning('Error changing file permissions: %s'%fn)
            self.log.logger.warning('%s'%detail)
            


    
    def readFileWithRaddoseKeywords(self):
        """
        Keywords of the form :
        
        key = value
        e.g.
        PHOSEC = 3.47e+12

        
        """
        
        fin = open(self.keysFileName, 'r')
        finContents = fin.readlines()
        
        self._keywords = {}

        for line in finContents :
            line = line.rstrip()
            if len(line) > 0 and not line.startswith('#') :
                entry = line.split('=')
                if entry is None or len(entry) is not 2 :
                    self.log.logger.error("Raddose keywords file malformed: " + self.keysFileName)
                else :
                    self._keywords[entry[0].strip()] = entry[1].strip()
        #print self._keywords
            
    
    def modifyRaddoseRunScript(self,raddoseShPathOut = './raddose.sh'):
        
        if self._keywords is  None :
            # means that raddose keys file is not present
            return
        
        self._newRaddoseExecutable = raddoseShPathOut
        
        fin = open(self._ednaRaddoseExecutable, 'r')
        finContents = fin.readlines()
        
        foutContents = []
        for line in finContents :
            if line.startswith("cd ") :
                pass
            elif line.startswith("/opt/pxsoft/bin/raddose") :
                tokens = line.split()            
                foutContents.append(tokens[0] + " << EOF\n")
            elif line.startswith("EOF"):
                break    
            elif line.startswith("END"):
                foutContents.append("END")
                foutContents.append("\n")
                foutContents.append("EOF")
                foutContents.append("\n")
            else :
                lineContents = line.split()
                if lineContents[0] in self._keywords.keys() :
                    foutContents.append(lineContents[0] + " " + self._keywords[lineContents[0]] + '\n')
                elif lineContents[0] == 'NRES' and 'NDNA' in self._keywords.keys() :
                    # exception to substitute NRES for NDNA 
                    foutContents.append('NDNA' + " " + self._keywords['NDNA'] + '\n')
                else :
                    foutContents.append(line)
        
        fout = open(raddoseShPathOut, 'w')
        fout.writelines(foutContents)
        fout.close()
        #os.chmod(raddoseShPathOut, 0755) 
        self.make_exe(raddoseShPathOut) 
        self.log.logger.debug('New raddose file written to: ' + raddoseShPathOut)
    
    def runAndParseRaddoseOutput(self):
        '''
        
        '''
        
        if self._keywords is  None :
            self.log.logger.error('runAndParseRaddoseOutput: no raddose kyywords present')
            return

        raddoseResult = self.run(self._newRaddoseExecutable )
        
        if raddoseResult is None :
            self.log.logger.error('There was a problem running raddose: ' + self._newRaddoseExecutable  )
        else :
            self.results = {}
            for line in raddoseResult.rstrip('\n').split('\n') :
                if line.startswith('Solvent Content') :
                    tokens = line.split()
                    self.results['solventContent'] = float(tokens[len(tokens)-1])
                if line.startswith('   Time in sec to reach Henderson limit') :
                    tokens = line.split()
                    self.realAbsorbedDoseRate = 20e6 / float(tokens[len(tokens)-1])
                    self.results['realAbsorbedDoseRate'] = self.realAbsorbedDoseRate
            self.log.logger.debug('Raddose finished: Solvent Content = %.2f , realAbsorbedDoseRate = %.2e' % (self.results['solventContent'],self.results['realAbsorbedDoseRate']) )
        

if __name__ == "__main__":
    raddose = Raddose('../Data/EDApplication_20101115-121936','../Data/raddose.keys')
    #raddose = Raddose('/data/id23eh1/inhouse/opid231/20101115/PROCESSED_DATA/Thaum2') 
    raddose.readFileWithRaddoseKeywords()
    raddose.modifyRaddoseRunScript('/tmp/raddose1.sh')
    raddose.runAndParseRaddoseOutput()
    print raddose.results
    
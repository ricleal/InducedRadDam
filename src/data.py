'''
Created on 5 Jun 2011

@author: leal
'''
import os
import numpy as np
import localLogger
import scipy.optimize as opt
import ini
import pickle
import pprint as pp


class Data():
    '''
    Holds a list of ditcionaries
    '''
    


    def __init__(self):
        '''
        Constructor
        '''
        self.log = localLogger.LocalLogger("data")
        self.listOfDicts = []
    
    def addListOfDcits(self,listOfDicts):
        
        # List of dictionaries raw
        self.listOfDicts.extend(listOfDicts)
        
    def mergeListOfDicts(self, listOfDicts, key):
        """
        merges 2 lists of dictionaries given a key
        
        if the key is does not exist, creates a new entry in the list
        
        """
        merged = {}
        for item in self.listOfDicts+listOfDicts:
            if item[key] in merged:
                merged[item[key]].update(item)
            else:
                merged[item[key]] = item
        self.listOfDicts = [val for (_, val) in merged.items()]
    
    def mergeListOfDictsIntersection(self, listOfDicts, key):
        """
        merges 2 lists of dictionaries given a key
        
        if the key does not exist, ignores it!
        
        """
        l1 = listOfDicts
        l2 = self.listOfDicts
        
        l1Values = [i[key] for i in l1]
        l2Values = [i[key] for i in l2]
        
        commonValues = set(l1Values).intersection( set(l2Values) )
        
        merged = {}
        for item in l1+l2:
            if item[key] in merged:
                merged[item[key]].update(item)
            elif item[key] in commonValues:
                merged[item[key]] = item
        self.listOfDicts = [val for (_, val) in merged.items()]
        
        
        
        
        

    
    def replicateDicToLisOfDicts(self,dic): 
        """
        This function receives a dictionary and will replicate it
        in all the entries of the dataAsListOfDicts
        """
        for i in self.listOfDicts:
            i.update(dic)
    
    def getListOfValuesFromKey(self,key):
        """
        
        Go through the list of dics and for the given key gets a list of values
        
        @return: list of values
        """
        output = []
        for dic in self.listOfDicts:
            try :
                output.append(dic[key])
            except KeyError:
                pass
        if len(output) == 0:
            self.log.logger.error('Key %s does not exist! Available keys: %s'%(key,self.__getAllKeys()))
        return np.array(output)
    
    def removeDicWhereKeyEquals(self,key,value):
        """
        Removes an element from the list where dic key = value
        """
        l = self.listOfDicts[:]
        for item in l :
            if item[key] == value :
                self.listOfDicts.remove(item)
    
    def removeDicWhereKeyNotIn(self,key,values):
        """
        Removes an element from the list where dic key is not in list of values
        """
#        UNSAFE!!!
#        for item in self.listOfDicts :
#            if item[key] not in values :
#                self.listOfDicts.remove(item)
        
        l = self.listOfDicts[:]
        for item in l:
            if item[key] not in values :
                self.listOfDicts.remove(item)
    
    def addListOfValuesWithKey(self,key,values):
        '''
        Add a list of values to all ditionaries in the list
        '''
        if len(values) > len(self.listOfDicts):
            self.log.logger.error('The list of values to add is larger than the list of dictionaries!')
            return
        
        for item,value in zip(self.listOfDicts,values) :
            item[key] = value

    
    
    def dumpToCsvFileAllKeys(self,csvFilePath):
        self.__dumpToCsvFile(csvFilePath,keys=self.__getAllKeys())
    
    def dumpToCsvFileAllKeysSorted(self,csvFilePath):
        self.__dumpToCsvFile(csvFilePath,keys=self.__getAllKeysSorted())
    
    def dumpToCsvFileCommonKeys(self,csvFilePath):
        self.__dumpToCsvFile(csvFilePath,keys=self.__getCommonKeys())
    
    
  

    ######################
    # Private methods
    ######################
    
    def __getAllKeys(self):
        """
        Get all unique Keys in the list of dics
        @return: list of keys
        """
        allKeysList = [item.keys() for item in self.listOfDicts]
        # Flatten the list
        allKeysListFlat= [item for sublist in allKeysList for item in sublist]
        # uniquefy
        allKeysUnique = list(set(allKeysListFlat))
        return allKeysUnique
    
    def __getAllKeysSorted(self):
        """
        Get all unique Keys in the list of dics
        @return: list of keys
        """
        allKeysList = [item.keys() for item in self.listOfDicts]
        # Flatten the list
        allKeysListFlat= [item for sublist in allKeysList for item in sublist]
        # uniquefy
        allKeysUnique = list(set(allKeysListFlat))
        
        allKeysUnique.sort()
        
        return allKeysUnique
    
    def __getCommonKeys(self):
        """
        Get only keys common to all dics
        @return: list of keys
        """
        
        # list of sets of keys
        allKeysList = [set(item.keys()) for item in self.listOfDicts]
        # Use * to break a list/tuple apart, so each element becomes a new argument.
        commonKeys = set.intersection(*allKeysList)
        
        return commonKeys


    def __dumpToCsvFile(self,csvFilePath,keys):
        """
        Dump file to CSV
        """
        f = open(csvFilePath, 'w')
        header = ','.join(keys)
        f.write(header+'\n')
        
        output = []
        for dic in self.listOfDicts:
            line = []
            for key in keys :
                try :
                    line.append(str(dic[key]))
                except KeyError:
                    line.append('')
            output.append(",".join(line))
            
        f.write('\n'.join(output))
        f.write('\n')
        f.close()
        self.log.logger.debug('CSV file dumped to: %s'%csvFilePath)
  
    


if __name__ == "__main__":
    
    
    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)
    
    
    listOfDicts = [{'subWedgeNumber':1,'action':'exposure','dose':1000},
                   {'subWedgeNumber':2,'action':'burn'},
                   {'subWedgeNumber':3,'action':'exposure','dose':2000},
                   {'subWedgeNumber':4,'action':'burn'},
                   {'subWedgeNumber':5,'action':'exposure','dose':3000},
                   {'subWedgeNumber':6,'action':'burn'},
                   {'subWedgeNumber':7,'action':'exposure','dose':4000}]
    
    listOfDicts2 = [{'subWedgeNumber':1,'action':'exposure','realDose':11000,'iOverSigma':10},
                   {'subWedgeNumber':3,'action':'exposure','realDose':21000,'iOverSigma':10},
                   {'subWedgeNumber':5,'action':'exposure','realDose':31000,'iOverSigma':10},
                   {'subWedgeNumber':7,'action':'exposure','realDose':41000,'iOverSigma':10}]

    d = Data()
    d.addListOfDcits(listOfDicts)
    #d.mergeListOfDicts(listOfDicts2, 'subWedgeNumber')
    d.mergeListOfDictsIntersection(listOfDicts2, 'subWedgeNumber')
    
    dummyDic = {'dummy1':1,'dummy2':2}
    d.replicateDicToLisOfDicts(dummyDic)
    
    pp.pprint(d.listOfDicts)
    
    print d.getListOfValuesFromKey('realDose')
    
    d.removeDicWhereKeyEquals('action','burn')
    
    d.dumpToCsvFileAllKeysSorted('/tmp/dicAll.csv')
    d.dumpToCsvFileCommonKeys('/tmp/dicCommon.csv')
    
    pp.pprint(d.listOfDicts)
    
    
    
    
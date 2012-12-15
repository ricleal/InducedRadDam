'''
Created on May 20, 2011

@author: leal
'''

import localLogger
import sys
import os
import os.path
import re
import wedgeHandler
import ini
import pprint as pp
import numpy as np
import pickle

class BurntWedgesHandler():
    '''

    NOT USED SO FAR!

    conventions:

    xxFolderName
    xxFolderPath
    xxFileName
    xxFilePath

    From a list of wedges parses the generated files after burning (best, xds...)


    '''


#    class Reflection():
#
#        '''
#
#        NOT USED
#
#        '''
#
#
#        def __init__(self,xdsReflectionLine):
#
#            self.hkl = []
#            self.psi = None
#            self.i = None
#            self.sigma = None
#            self.resolution = None
#            self.xdsReflectionLine = xdsReflectionLine
#
#            self.parseXdsReflectionLine()
#
#        def parseXdsReflectionLine(self,xdsReflectionLine=None):
#
#            if xdsReflectionLine is None:
#                xdsReflectionLine = self.xdsReflectionLine
#
#            self.hkl = xdsReflectionLine[:3]
#            self.psi = xdsReflectionLine[11]
#            self.i = xdsReflectionLine[3]
#            self.sigma = xdsReflectionLine[4]
#
#        def setResolution(self,d):
#            self.resolution = d
#
#        def same(self, reflection):
#            if self.hkl == reflection.hkl and \
#                reflection.psi > self.psi -2 or reflection.psi < self.psi + 2 :
#                return True
#            else :
#                return False





    def __init__(self, wedge):
        '''
        Constructor:

        @param wedge: wedgeHandler - the folder name contents parsed...

        '''
        self.wedge = wedge

        self.log = localLogger.LocalLogger("burntWedge")
        self.log.logger.debug("BurntWedgesHandler...")

        self.wedgeList = []

    def parseWedges(self,wedgeNumbersListToProcess,resolution):
        """
        Parses the XDS and Best log files and builds a dictionary
        with statists of corresponding wedge : self.wedgeList

        """

        recordList = []

        for i in wedgeNumbersListToProcess :

            record = {}

            record['subWedgeNumber'] = i
            record['resolution'] =  resolution

            wedgeFolderPath = self.wedge.getWedgeFolderPath(i)
            
            # BEST
            bestLogFilePath = os.path.join(wedgeFolderPath,ini.Ini().getPar("BEST","best_log_file"))
            bestRecord = self.__parseBestLogFile(bestLogFilePath)
            record.update(bestRecord)
            #pp.pprint(record)

            self.reciprocalMat = self.__crystGen(self.currentCell)

#            # get crystal type
#            self.crystalSystemName = self.__getCrystalSystemName(self.currentCell)
#            record['crystalSystemName'] = self.crystalSystemName
#            self.log.logger.debug("Crystal System Name: " + self.crystalSystemName)

            # XDS

            xdsLogFilePath = os.path.join(wedgeFolderPath,ini.Ini().getPar("XDS","xds_log_file"))
            xdsRecord = self.__parseXdsCorrectLogFile(xdsLogFilePath)
            record.update(xdsRecord)

            xdsIntensitiesFilePath = os.path.join(wedgeFolderPath,ini.Ini().getPar("XDS","xds_intensities_file"))
            # Parse hkl file and calculate resolution per reflection
            reflectionList = self.__parseXdsXhlFile(xdsIntensitiesFilePath)

            xdsRecord = self.__calculateXDSIntegratedIntensity(reflectionList,resolution)
            record.update(xdsRecord)
            
            if len(bestRecord) > 0 and len(xdsRecord) > 0 and reflectionList is not None and  len(reflectionList) > 0:
                recordList.append(record)

        self.wedgeList = recordList
        #self.__createRelativeIntensityField('relativeScale')
        #self.__createRelativeOverallBFactorField('overallBFactor')
#        for resolution in resolutionRange :
#            self.__createRelativeAverageIntegratedIntensityField(self.buildAverageIntegratedIntensityFieldName(resolution))



        #self.log.logger.debug(pprint.pformat(self.wedgeList))


    def __parseBestLogFile(self, bestLogFilePath):
        """
        Parses best log file

                          Scaling results
                          ===============
         Relative scale       :   73.21
         Overall B-factor     :  24.10 Angstrom^2
         B-factor eigenvalues :  24.10  24.10  24.10 Angstrom^2

        Crystal
         Space Group                      : I 2 3
         Cell                             :  78.94  78.94  78.94  90.00  90.00  90.00
         Mosaicity                        : 0.29 degree

        """

        record = {}
        
        self.log.logger.debug("Parsing: " + bestLogFilePath)
        # Put in this array pairs of <name>:<value>
        parsedData=[]

        if os.path.exists(bestLogFilePath):
            infile = open(bestLogFilePath,"r")
            for line in infile:
                if line.find(':') >=0 :
                    parsedData.append(line.rstrip().split(':'))
        else:
            self.log.logger.warning('Best file does not exist: %s'%bestLogFilePath)
            return record
        

        #
        

        for t in parsedData:
            t[0]=t[0].strip()
            if t[0].find("Relative scale")>=0 :
                record["relativeScale"] = float(t[1].strip())
            elif t[0].find("Overall B-factor")>=0 :
                record["overallBFactor"] = float(t[1].strip().split()[0])
            elif t[0].find("Cell")>=0 :
                tokens = t[1].strip().split()
                record['cell_length_a']= float(tokens[0])
                record['cell_length_b']= float(tokens[1])
                record['cell_length_c']= float(tokens[2])
                record['cell_angle_alpha']= float(tokens[3])
                record['cell_angle_beta']=float(tokens[4])
                record['cell_angle_gamma']= float(tokens[5])
                self.currentCell = [float(i) for i in tokens[:6]]

            elif t[0].find("Mosaicity")>=0 :
                record["mosaicity"] = float(t[1].strip().split()[0])
        if not record : # empty!
            self.log.logger.warning("Nothing was parsed from best log file!")
        else :
            self.log.logger.debug("Overall B-factor = %.2f : Relative scale = %.2f" % (record["overallBFactor"],record["relativeScale"]))
            self.log.logger.debug("Cell:" + " ".join(["%.2f"%i for i in self.currentCell]) )


        return record


    def __parseXdsCorrectLogFile(self,xdsLogFilePath):
        """
          COMPLETENESS AND QUALITY OF DATA SET
          ------------------------------------

 R-FACTOR
 observed = (SUM(ABS(I(h,i)-I(h))))/(SUM(I(h,i)))
 expected = expected R-FACTOR derived from Sigma(I)

 COMPARED = number of reflections used for calculating R-FACTOR
 I/SIGMA  = mean of intensity/Sigma(I) of unique reflections
            (after merging symmetry-related observations)
 Sigma(I) = standard deviation of reflection intensity I
            estimated from sample statistics

 R-meas   = redundancy independent R-factor (intensities)
 Rmrgd-F  = quality of amplitudes (F) of this data set
            For definition of R-meas and Rmrgd-F see
            Diederichs & Karplus (1997), Nature Struct. Biol. 4, 269-275.

 Anomal   = mean correlation factor between two random subsets
  Corr      of anomalous intensity differences
 SigAno   = mean anomalous difference in units of its estimated
            standard deviation (|F(+)-F(-)|/Sigma). F(+), F(-)
            are structure factor estimates obtained from the
            merged intensity observations in each parity class.
  Nano    = Number of unique reflections used to calculate
            Anomal_Corr & SigAno. At least two observations
            for each (+ and -) parity are required.


 SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION
 RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  Rmrgd-F  Anomal  SigAno   Nano
   LIMIT     OBSERVED  UNIQUE  POSSIBLE     OF DATA   observed  expected                                      Corr

     4.80         139     124       449       27.6%       7.3%      8.0%       29    7.00    10.1%     7.9%     0%   0.000       0
     3.41         256     227       744       30.5%       9.0%      8.6%       56    6.58    12.5%    10.5%     0%   0.000       0
     2.79         315     277       948       29.2%       8.3%      9.0%       76    5.52    11.8%     9.7%     0%   0.000       0
     2.42         393     337      1111       30.3%      10.9%     11.1%      107    4.50    15.1%    16.3%     0%   0.000       0
     2.17         432     359      1254       28.6%      16.3%     17.6%      138    2.91    22.4%    23.8%     0%   0.000       0
     1.98         366     332      1386       24.0%      20.0%     24.3%       65    1.87    27.6%    30.0%     0%   0.000       0
     1.83         212     203      1484       13.7%      20.0%     44.7%       17    0.96    27.2%    38.9%     0%   0.000       0
     1.71         117     115      1585        7.3%      53.1%     92.4%        4    0.56    75.1%   137.4%     0%   0.000       0
     1.62          49      49      1707        2.9%     -99.9%    -99.9%        0  -99.00   -99.9%   -99.9%     0%   0.000       0
    total        2279    2023     10668       19.0%       9.4%     10.0%      492    3.63    13.1%    15.0%     0%   0.000       0


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES    2279
 NUMBER OF REJECTED MISFITS                               0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                  0
 NUMBER OF ACCEPTED OBSERVATIONS                       2279
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                 2023




        """
        self.log.logger.debug("Parsing: " + xdsLogFilePath)

        record = {}
        if os.path.exists(xdsLogFilePath) :
            infile = open(xdsLogFilePath,"r")
            insideTableFlag = False
            for line in infile:
                if insideTableFlag is True:
                    if line.strip().startswith('total'):
                        tokens = line.strip().split()
                        #print tokens
                        record['numberOfReflectionsObserved'] = float(tokens[1])
                        record['completenessOfData'] = float(tokens[4].replace('%',''))/100
                        record['iOverSigma'] = float(tokens[8])
                        record['rMeas'] = float(tokens[9].replace('%',''))/100
                        break
                if line.find('COMPLETENESS AND QUALITY OF DATA SET') >= 0 :
                    insideTableFlag = True
        else: 
            self.log.logger.warning('XDS Correct file does not exist: %s'%xdsLogFilePath)
            return record

        if not record : # empty!
            self.log.logger.warning("Nothing was parsed from XDS CORRECT file! XDS may have failed...")
        else :
            self.log.logger.debug("Completeness = %.2f : N. of Reflections = %d : I/Sig(I) = %.2f : Rmeas = %.2f"\
                                  %(record['completenessOfData'],record['numberOfReflectionsObserved'],record['iOverSigma'],record['rMeas'] ))
        return record


    def __parseXdsXhlFile(self,xdsIntensitiesFilePath):
        """

        reads the XDS_ASCII.HKL and return a list of reclections of the format:

        Saves the list to the file : xds_reflections_out_file
        h k l I sigma(I) resolution

       !NUMBER_OF_ITEMS_IN_EACH_DATA_RECORD=12
        !ITEM_H=1
        !ITEM_K=2
        !ITEM_L=3
        !ITEM_IOBS=4
        !ITEM_SIGMA(IOBS)=5
        !ITEM_XD=6
        !ITEM_YD=7
        !ITEM_ZD=8
        !ITEM_RLP=9
        !ITEM_PEAK=10
        !ITEM_CORR=11
        !ITEM_PSI=12

        """

        reflectionList = []
        if os.path.exists(xdsIntensitiesFilePath) is False:
            self.log.logger.warning('XDS HKL file does not exist: %s'%xdsIntensitiesFilePath)
            return reflectionList
        else :
            inp = open(xdsIntensitiesFilePath,"r")
            lines = inp.readlines()
            inp.close()

            spaceGroupNumber = None
            header=True
            for line in lines:
                if line.find("!END_OF_DATA") >= 0 :
                    self.log.logger.debug("File parsed successfully: " + xdsIntensitiesFilePath)
                    # Writes list of reflection to a file
                    wedgeBasePath = os.path.dirname(xdsIntensitiesFilePath)
                    outFilePath = os.path.join(wedgeBasePath,ini.Ini().getPar("XDS","xds_reflections_out_file"))
                    outFile = open(outFilePath,"wb")

                    self.log.logger.info("Dumping reflections file to: " +  outFilePath)
                    #pp.pprint(reflectionList,depth=2)
                    pickle.dump(reflectionList, outFile)

                    break
                if header is False:
                    # Inside the list of reflection
                    lineContents = line.split()
                    reflection = [ int(i) for i in lineContents[:3]]
                    intensity = float(lineContents[3])
                    sigma = float(lineContents[4])
                    resolution = self.__getD(reflection) #self.__getD(reflection,self.currentCell, spaceGroupNumber)
                    # put all in the same list

                    #print '%5d%5d%5d %8.2f %.2f' %(reflection[0],reflection[1],reflection[2],float(lineContents[-1]),resolution)

                    reflection.append(intensity)
                    reflection.append(sigma)
                    reflection.append(resolution)
                    reflectionList.append(reflection)
                if line.find("!END_OF_HEADER") >= 0 :
                    header=False
#                elif line.find("SPACE_GROUP_NUMBER") >= 0 :
#                    spaceGroupNumber =  int(line.split()[1])
#                    #print "spaceGroupNumber ->", spaceGroupNumber


        return reflectionList

    def __calculateXDSIntegratedIntensity(self,reflectionList,resolution):

        """
        Calculates the integrated intensitity from the diffraction pattern

        """
        
        record = {}
        
        if reflectionList is None or len(reflectionList) == 0:
            return record

        iSum = 0 # intensity sum
        rSum = 0 # reflections sum
        for entry in reflectionList:
            h,k,l,i,sigma,res = entry
            if i > 0 and sigma > 0 :
                if resolution is None or res >= resolution:
                    iSum += i
                    rSum += 1
                else :
                    #print 'Not including reflection', reflection
                    pass


        averageISum = iSum / rSum


        self.log.logger.debug("Integrated intensities above %.2f A : Sum(I) = %10.1f ; <Sum(I)> = %10.1f ; N.reflection = %6d"\
                              %(resolution,iSum,averageISum,rSum))

        #self.log.logger.debug("Average Sum(I) below %.2f A in XDS_ASCII.HKL: %d" % (resolution,averageISum))
#        record[self.buildAverageIntegratedIntensityFieldName(resolution)] = averageISum
#        record[self.buildAverageIntegratedIntensityFieldName(resolution,'numberOfReflections')] = rSum
        record['averageIntegratedIntensity'] = averageISum
        record['numberOfReflections'] = rSum
        return record

#    def buildAverageIntegratedIntensityFieldName(self,resolution,prefix="averageIntegratedIntensity"):
#        """
#        Builds average intensity header
#        """
#        return prefix+"_%.2f"%(resolution)
#
#    def resolutionSuffixFieldName(self,resolution):
#        """
#        Builds average intensity header
#        """
#        return "_%.2f"%(resolution)

    def createRelativeScaleField(self,s0,relativeScale):
        """
        Best does not output relative scale: relativeScale
        I only supllies the Scale factor applied to the data!

        it has to calculated from the field specified in the parameter field

        @param field: field parsed from best
        @param s0: will the S0 in the fitting of the data: s0 x exp( -(alpha * dose)**s ) 
        
        @return: invRelativeScale
        """

        maxScale = 1/s0
        return  1 / relativeScale / maxScale
    

    def createRelativeAverageIntegratedIntensityField(self,s0,s1,averageIntegratedIntensity):
        
        
        """
        
        creates RelativeAverageIntegratedIntensity 
        
        Divides the Intensity by I0 where, I0 is:
        I(D=0) = I(D1)* S0/S(D1)
        Where S0 and S(Di) belong to the fitting of the scale: S(D) = S0 * exp((D*\alpha)^2)
        
        @return: relativeAverageIntegratedIntensity
        
        """
        
        IForDEqualsTo0 = averageIntegratedIntensity[0] * s0/s1
        relativeAverageIntegratedIntensity = np.array(averageIntegratedIntensity) / IForDEqualsTo0
        
        return relativeAverageIntegratedIntensity

    def createRelativeOverallBFactorField(self,bFactor0,overallBFactors):
        """
        Create Relative Bfactor
        
        @return relativeOverallBFactor
        
        """


        relativeBFactors = overallBFactors - bFactor0
        
        return relativeBFactors

     

#    def __getD(self, hkl, cell,spaceGroupNumber):
#        """
#
#        Get the d distance from a reflection, i.i, resolution in A of a reflection
#
#        http://www.ruppweb.org/xray/tutorial/spcdiff.htm
#
#        TODO: needs to be optimised
#
#        """
#
#        h,k,l = hkl
#        a,b,c,alpha,beta,gamma = cell
#
#
#
#        # http://pd.chem.ucl.ac.uk/pdnn/unit1/unintro.htm
#        #if self.crystalSystemName == 'triclinic' :
#        if spaceGroupNumber in [1,2] :
#            # to optimise. Calculate this in advance
#            cosAlpha = np.cos(alpha)
#            #sinAlpha = np.sin(alpha)
#            cosBeta = np.cosBeta
#            #sinBeta = np.sinBeta
#            cosGamma = np.cos(gamma)
#            #sinGamma = np.sin(gamma)
#            s = np.square(h) * np.square(1/a) + np.square(k) * np.square(1/b) + np.square(l) * np.square(1/c) + \
#                2 * k * l * (1/b) * (1/c) * cosAlpha + \
#                2 * h * l * (1/a) * (1/c) * cosBeta + \
#                2 * h * k * (1/a) * (1/b) * cosGamma
#        elif spaceGroupNumber in range(3,16) : #self.crystalSystemName ==  'monoclinic' :
#
#
#            sinBeta = np.sinBeta
#            cosBeta = np.cosBeta
#
#            # 1/d2 = h2 / (a2 sin2 beta) + k2 / b2 + l2 / (c2 sin2 beta) - 2 hl cos beta / (ac sin2 beta)
#            s = np.square(h) / (np.square(a) * np.square(sinBeta) ) + \
#                np.square(k) / np.square(b) + \
#                np.square(l) / (np.square(c) * np.square(sinBeta) ) - \
#                2 * h * l * cosBeta / (a * c * np.square(sinBeta) )
#
#
#        elif spaceGroupNumber in range(16,75) : #elif self.crystalSystemName ==  'orthorhombic' :
#            # 1/d2 = h2 / a2 + k2 / b2 + l2 / c2
#            s = np.square(h) / np.square(a) + np.square(k) / np.square(b) + np.square(l) / np.square(c)
#
#        elif spaceGroupNumber in range(75,143) : #elif self.crystalSystemName ==  'tetragonal':
#            # (h2 + k2) / a2 + l2 / c2
#            s = (np.square(h) + np.square(k) ) / np.square(a) + np.square(l) / np.square(c)
#        elif spaceGroupNumber in range(143,168) : #elif self.crystalSystemName ==  'trigonal':
#            # 1/d2 = a*2 {(h2 + k2 + l2) + 2 cosalfa (kl + hl + hk)}
#            cosAlpha = np.cos(alpha)
#            s = 1/np.square(a) * ( (np.square(h) + np.square(k) + np.square(l))  + 2 * cosAlpha * (k*l + h*l + h*k) )
#        elif spaceGroupNumber in range(168,195) : #elif self.crystalSystemName ==  'hexagonal':
#            #     1/d2 = 4 (h2 + hk + k2) / 3a2 + l2 / c2
#            s = 4 * ( np.square(h) + h * k + np.square(k) ) / (3 * np.square(a))  +  np.square(l) / np.square(c)
#        elif spaceGroupNumber in range(195,231) : #elif self.crystalSystemName ==  'cubic':
#            # Cubic    1/d2 = (h2 + k2 + l2) / a2
#            s = (np.square(h) + np.square(k) + np.square(l)) / np.square(a)
#        else :
#            self.log.logger.error("Crystal system name not recognized: " + self.crystalSystemName)
#            sys.exit(-2)
#
#

#        s = (np.square(h)/np.square(a) * np.square(sinAlpha) + np.square(k)/np.square(b) * np.square(sinBeta) +
#             np.square(l)/np.square(c) * np.square(sinGamma) +
#             (2*k*l)/(b*c) * (cosBeta*cosGamma-cosAlpha) +
#             (2*h*l)/(a*c) * (cosAlpha*cosGamma-cosBeta) +
#             (2*h*k)/(a*b) * (cosAlpha*cosBeta-cosGamma)
#             )/(1 - np.square(cosAlpha) * np.square(cosBeta) -np.square(cosGamma) + 2*cosAlpha*cosBeta*cosGamma)
#
#        d = 1/np.sqrt(s)


#
#

#        d = np.sqrt(1/s)
#
#        #print '%5d%5d%5d  %.2f' %(h,k,l,d)
#        return d

#    def __getCrystalSystemName(self,cell):
#        """
#        Get crystal system Name from unit cell paramms:
#
#        Triclinic
#        Monoclinic
#        Orthorhombic
#        Tetragonal
#        Trigonal
#        Hexagonal
#        Cubic
#
#        """
#
#        a,b,c,alpha,beta,gamma = cell
#
#        if a != b and b != c and alpha != beta and beta != gamma :
#            return 'triclinic'
#        elif a != b and b != c and alpha == gamma and gamma == 90 and beta != 90 :
#            return 'monoclinic'
#        elif a != b and b != c and alpha == beta and beta == gamma and gamma == 90 :
#            return 'orthorhombic'
#        elif a == b and b != c and alpha == beta and beta == gamma and gamma == 90 :
#            return 'tetragonal'
#        elif a == b and b == c and alpha == beta and beta == gamma and gamma != 90 :
#            return 'trigonal'
#        elif a == b and b != c and alpha == beta and beta == 90 and gamma == 120 :
#            return 'hexagonal'
#        elif a == b and b == c and alpha == beta and beta == gamma and gamma == 90 :
#            return 'cubic'
#        else :
#            self.log.logger.error("Crystal system not recognised for cell: " + cell)
#            sys.exit(-2)

    def __getD(self, hkl) :

        self.reciprocalMat

        h,k,l = hkl

        hklM = np.matrix([h,k,l])
        hklMT = np.transpose(hklM)

        # s = h**2 = xh**2 + yk**2 + zl**2
        s = np.sum(np.square(self.reciprocalMat * hklMT))

        d = np.sqrt(1/s)

        #print '%5d%5d%5d  %8.2f %8.2f' %(h,k,l,s,d)
        return d


    def __crystGen(self,cell):
        """
        c-------------------------------------------------
        c    Callculation of reciprocal lattice parameters and
        c     orthogonal matrix of crystal orientation
        c    Am(3,3) -  3*3 - matrics
        c       a*  b*cos(gama*)  c*cos(beta*)
        c       0   b*sin(gama*) -c*sin(beta*)cosAlpha
        c       0       0         1/c
        c
        c===================================================
        """

        a,b,c,alpha,beta,gamma = cell

        alpha = alpha * np.pi/180
        beta = beta * np.pi/180
        gamma = gamma * np.pi/180

        cosAlpha = np.cos(alpha)
        sinAlpha = np.sin(alpha)
        cosBeta = np.cos(beta)
        sinBeta = np.sin(beta)
        cosGamma = np.cos(gamma)
        sinGamma = np.sin(gamma)

        vol=a*b*c*np.sqrt(1.-cosAlpha**2-cosBeta**2-cosGamma**2+2.*cosAlpha*cosBeta*cosGamma)

        ar=b*c*sinAlpha/vol
        br=a*c*sinBeta/vol
        cr=a*b*sinGamma/vol

        cosalfar=(cosBeta*cosGamma-cosAlpha)/(sinBeta*sinGamma)
        cosbetar=(cosAlpha*cosGamma-cosBeta)/(sinAlpha*sinGamma)
        cosgamar=(cosAlpha*cosBeta-cosGamma)/(sinAlpha*sinBeta)

        alfar=np.arccos(cosalfar)
        betar=np.arccos(cosbetar)
        gamar=np.arccos(cosgamar)

        am = np.matrix([[ar, br*np.cos(gamar), cr*np.cos(betar)],
                        [ 0.0, br*np.sin(gamar), -cr*np.sin(betar)*cosAlpha],
                        [ 0.0, 0.0, 1.0/c]])

        #print am

        return am



if __name__ == '__main__':

    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)

    #w = wedgeHandler.WedgeHandler('/mntdirect/_data_id23eh1_inhouse/opid231/20101106/PROCESSED_DATA/LYS3_M_ROOM/xds_t4w21_run1_1/')
    w = wedgeHandler.WedgeHandler('../Data/xds_in1w21_run1_1/')
    #w.buildEdnaFolderPath('EDApplication_20101106-193059')
    w.buildEdnaFolderPath('EDApplication_20110515-160120')

    b = BurntWedgesHandler(w)
    #b.parseWedges(range(1,22,2),[3,2.75,2.5])
    b.parseWedges([1,3],[4,3.5,3,2.75,2.5,0])

    #pp.pprint(b.wedgeList,depth=2)
            



'''
Created on Mar 1, 2012

@author: leal
'''

import numpy as np
import localLogger
import scipy.optimize as opt

class Fitting(object):
    '''
    classdocs
    '''


    def __init__(self,x,y):
        '''
        Constructor
        '''
        
        self.log = localLogger.LocalLogger("fitting")
        
        self.discrete_x = x
        self.discrete_y = y
        
        self.continuous_x = None
        self.continuous_y = None
        
        self.function = None
        self.coefficients = None
        self.error = None
        
        #self.log.logger.debug('Data to Fit: \nX: %s\nY: %s'%(x,y))
    
    def setContinuousX(self,start=0,end=None,n_points=100):
        self.n_points = n_points
        if end is None :
            #end = self.discrete_x[-1]
            end = np.max(self.discrete_x)
        
        self.continuous_x = np.linspace(start,end,n_points)
    
        
    def linearFitting2Coeffs(self):
        self.function = np.polyval
        self.coefficients = np.polyfit(self.discrete_x,self.discrete_y, 1)
    
    
    def linearFitting1Coeff(self):
        
        self.function = self.funcLinear1coeff
        residuals = self.residualsLinear1coeff
        
        # Estimate a,b
        a,b = np.polyfit(self.discrete_x,self.discrete_y, 1)

        #initial guess
        p0=[a]
                
        #self.log.logger.debug("Guess exponential function: %.2e * exp(%.2e * x) + %.2e" % (p0[0],p0[1],0))
        plsq = opt.fmin(residuals, p0, args=(self.discrete_x,self.discrete_y), maxiter=10000, maxfun=10000,disp=False)
        #self.log.logger.debug("Exponential fit function: %.2e * exp(%.2e * x) + %.2e" % (plsq[0],plsq[1],plsq[2]))
        #print plsq
        
        self.coefficients = plsq
    
    def exponentialFitting1Coeff(self):
        
        self.function = self.funcExponential1coeffs
        residuals = self.residualsExponential1coeffs
        
        # Estimate a and b, assuming c = 0
        # y = A * exp(B * x) can be linearized by fitting log(y) = log(A * exp(B * x)) = B * x + log(A)
        # y2 = B * x + log(A)
        y2 = np.log(self.discrete_y)
        b, log2 = np.polyfit(self.discrete_x, y2, 1)
        a = np.exp(log2)

        #initial guess
        p0=[b]
                
        #self.log.logger.debug("Guess exponential function: %.2e * exp(%.2e * x) + %.2e" % (p0[0],p0[1],0))
        plsq = opt.fmin(residuals, p0, args=(self.discrete_x,self.discrete_y), maxiter=10000, maxfun=10000,disp=False)
        #self.log.logger.debug("Exponential fit function: %.2e * exp(%.2e * x) + %.2e" % (plsq[0],plsq[1],plsq[2]))
        #print plsq
        
        self.coefficients = plsq
    
    
    def exponentialFitting3Coeffs(self):
        
        self.function = self.funcExponential3coeffs
        residuals = self.residualsExponential3coeffs
        
        # Estimate a and b, assuming c = 0
        # y = A * exp(B * x) can be linearized by fitting log(y) = log(A * exp(B * x)) = B * x + log(A)
        # y2 = B * x + log(A)
        y2 = np.log(self.discrete_y)
        b, log2 = np.polyfit(self.discrete_x, y2, 1)
        a = np.exp(log2)

        #initial guess
        p0=[a,b,0]
                
        #self.log.logger.debug("Guess exponential function: %.2e * exp(%.2e * x) + %.2e" % (p0[0],p0[1],0))
        plsq = opt.fmin(residuals, p0, args=(self.discrete_x,self.discrete_y), maxiter=10000, maxfun=10000,disp=False)
        #self.log.logger.debug("Exponential fit function: %.2e * exp(%.2e * x) + %.2e" % (plsq[0],plsq[1],plsq[2]))
        #print plsq
        
        self.coefficients = plsq
    
    def exponentialSquared2coeffsFitting(self):
        
        
        self.function = self.funcExponentialSquared2coeffs
        residuals = self.residualsExponentialSquared2coeffs
        
        # Estimate a and b, assuming c = 0
        # y = A * exp(B * x) can be linearized by fitting log(y) = log(A * exp(B * x)) = B * x + log(A)
        # y2 = B * x + log(A)
        y2 = np.log(self.discrete_y)
        b, log2 = np.polyfit(self.discrete_x, y2, 1)
        a = np.exp(log2)

        #initial guess
        p0=[a,b]
                
        #self.log.logger.debug("Guess exponential function: %.2e * exp(%.2e * x) + %.2e" % (p0[0],p0[1],0))
        plsq = opt.fmin(residuals, p0, args=(self.discrete_x,self.discrete_y), maxiter=10000, maxfun=10000,disp=False)
        #self.log.logger.debug("Exponential fit function: %.2e * exp(%.2e * x) + %.2e" % (plsq[0],plsq[1],plsq[2]))
        #print plsq
        
        self.coefficients = plsq
    
    def exponentialSquared1coeffFitting(self):
        
        
        self.function = self.funcExponentialSquared1coeff
        residuals = self.residualsExponentialSquared1coeff
        
        # Estimate a and b, assuming c = 0
        # y = A * exp(B * x) can be linearized by fitting log(y) = log(A * exp(B * x)) = B * x + log(A)
        # y2 = B * x + log(A)
        y2 = np.log(self.discrete_y)
        b, log2 = np.polyfit(self.discrete_x, y2, 1)
        a = np.exp(log2)

        #initial guess
        p0=[a,b]
                
        #self.log.logger.debug("Guess exponential function: %.2e * exp(%.2e * x) + %.2e" % (p0[0],p0[1],0))
        plsq = opt.fmin(residuals, p0, args=(self.discrete_x,self.discrete_y), maxiter=10000, maxfun=10000,disp=False)
        #self.log.logger.debug("Exponential fit function: %.2e * exp(%.2e * x) + %.2e" % (plsq[0],plsq[1],plsq[2]))
        #print plsq
        
        self.coefficients = plsq
    
    def exponentialSquared1CoeffsNegativeFitting(self):
        
        
        self.function = self.funcExponentialSquaredNegative1coeffs
        residuals = self.residualsExponentialSquaredNegative1coeffs
        
        # Estimate a and b, assuming c = 0
        # y = A * exp(B * x) can be linearized by fitting y = log(A * exp(B * x)) = B * x + log(A)
        y2 = np.log(self.discrete_y)
        b, log2 = np.polyfit(self.discrete_x, y2, 1)
        a = np.exp(log2)

        #initial guess
        p0=[b]
                
        #self.log.logger.debug("Guess exponential function: %.2e * exp(%.2e * x) + %.2e" % (p0[0],p0[1],0))
        plsq = opt.fmin(residuals, p0, args=(self.discrete_x,self.discrete_y), maxiter=10000, maxfun=10000,disp=False)
        #self.log.logger.debug("Exponential fit function: %.2e * exp(%.2e * x) + %.2e" % (plsq[0],plsq[1],plsq[2]))
        #print plsq
        
        self.coefficients = plsq

    
    def determineError(self):
        fittedPoints = self.function(self.coefficients,self.discrete_x)
        self.error = np.sqrt(sum((fittedPoints-self.discrete_y )**2)/len(fittedPoints))
        self.log.logger.debug("Fitting error: %.2e for %2d points."%(self.error,len(fittedPoints)))
        
    
    def setContinuousY(self):
        self.continuous_y = self.function(self.coefficients,self.continuous_x)
    
    
    
    ##########################    
    
    #
    def funcExponential3coeffs(self,coeffs,x):
        a,b,c = coeffs
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return a*np.exp( b*x )+c
    
    def residualsExponential3coeffs(self,p,x,y):
        w=p[0]*np.exp( p[1]*x ) + p[2]
        err=w-y
        err=err**2
        b=sum(err)
        return b
    
    #
    def funcExponential2coeffs(self,coeffs,x):
        a,b = coeffs
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return a*np.exp( b*x )
    
    def residualsExponential2coeffs(self,p,x,y):
        w=p[0]*np.exp( p[1]*x )
        err=w-y
        err=err**2
        b=sum(err)
        return b
   
    def funcExponential1coeffs(self,coeffs,x):
        b = coeffs[0]
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return np.exp( b*x )
    
    def residualsExponential1coeffs(self,p,x,y):
        w=np.exp( p[0]*x )
        err=w-y
        err=err**2
        b=sum(err)
        return b
    
    
    #
    def funcExponentialSquared3coeffs(self,coeffs,x):
        a,b,c = coeffs
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return a*np.exp( (b*x)**2 )+c
    
    def residualsExponentialSquared3coeffs(self,p,x,y):
        w=p[0]*np.exp( (p[1]*x)**2 ) + p[2]
        err=w-y
        err=err**2
        b=sum(err)
        return b
    #
    def funcExponentialSquared2coeffs(self,coeffs,x):
        a,b = coeffs
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return a*np.exp( (b*x)**2 )
    
    def residualsExponentialSquared2coeffs(self,p,x,y):
        w=p[0]*np.exp( (p[1]*x)**2 )
        err=w-y
        err=err**2
        b=sum(err)
        return b
    
    #
    def funcExponentialSquared1coeff(self,coeffs,x):
        b = coeffs[0]
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return np.exp((b*x)**2 )
    
    def residualsExponentialSquared1coeff(self,p,x,y):
        w=np.exp( (p[0]*x)**2 )
        err=w-y
        err=err**2
        b=sum(err)
        return b        
    
    #
    def funcExponentialSquaredNegative1coeffs(self,coeffs,x):
        b = coeffs[0]
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return np.exp(-(b*x)**2 )
    
    def residualsExponentialSquaredNegative1coeffs(self,p,x,y):
        w=np.exp( -(p[0]*x)**2 )
        err=w-y
        err=err**2
        b=sum(err)
        return b        
    
    
    #
    def funcLinear1coeff(self,coeffs,x):
        b = coeffs[0]
        # a - y coordinate where x=0
        # b - curve inclination (large values, high inclination
        # c - moves curve in y axis
        return b*x
    
    def residualsLinear1coeff(self,p,x,y):
        w=p[0]*x
        err=w-y
        err=err**2
        b=sum(err)
        return b
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    ######
    # Do it all
    ######
    
    def doMultipleLinearFitting1Coeff(self):
        """
        
        Going throught all the data and calculates the fitting since the first 2 points
        
        @return: a list with the slopes of the linear fitting
        """
        
        self.setContinuousX()
        slopes = []
        slopes.append(0)
        x= self.discrete_x
        y= self.discrete_y
        for i in range(2,len(x)+1):
            temp = Fitting(x[:i],y[:i])
            temp.linearFitting1Coeff()
            slopes.append(temp.coefficients[0])
        # I know I am going to repeat the same fitting but its simpler
        self.linearFitting1Coeff()     
        self.setContinuousY()
        self.determineError()
        
        return slopes
    
    def doMultipleLinearFitting2Coeffs(self):
        """
        
        Going throught all the data and calculates the fitting since the first 2 points
        
        @return: a list with the slopes of the linear fitting
        """
        
        self.setContinuousX()
        slopes = []
        slopes.append(0)
        x0 = []
        x0.append(0)
        
        x= self.discrete_x
        y= self.discrete_y
        for i in range(2,len(x)+1):
            temp = Fitting(x[:i],y[:i])
            temp.linearFitting2Coeffs()
            slopes.append(temp.coefficients[0])
            x0.append(temp.coefficients[1])
        # I know I am going to repeat the same fitting but its simpler
        self.linearFitting2Coeffs()    
        self.setContinuousY()
        self.determineError()
        
        return slopes,x0

    
    def doMultipleExponentialSquared2coeffsFitting(self):
        """
        
        Going through all the data and calculates the fitting since the first 2 points
        
        @return: 2 lists of the coefficients of the fitting: A exp((Bx)**2)
        """
        
        
        self.setContinuousX()
        coeffA = []
        coeffA.append(0)
        coeffB = []
        coeffB.append(0)
        
        x= self.discrete_x
        y= self.discrete_y
        for i in range(2,len(x)+1):
            temp = Fitting(x[:i],y[:i])
            temp.exponentialSquared2coeffsFitting()
            coeffA.append(temp.coefficients[0])
            coeffB.append(temp.coefficients[1])
        # I know I am going to repeat the same fitting but its simpler
        self.exponentialSquared2coeffsFitting()        
        self.setContinuousY()
        self.determineError()
        
        return coeffA,coeffB
    
        
    def doMultipleExponentialFittingReturnHalfY(self):
        """
        
        Going through all the data and calculates the fitting since the first 2 points
        
        @return: return a list of X values when Y is halved
        """
        
        
        def invFunc(coeffs,y):
            #a,b,c = coeffs
            # y = a*exp(b*x)+c
            # 
            #return np.log((y - c)/a)/ b
            b = coeffs[0]
            return np.log(y)/b        
        
        
        self.setContinuousX()
        xForYHalveds = []
        xForYHalveds.append(0)
        
        halfY = np.max(self.discrete_y)/2
    
        x= self.discrete_x
        y= self.discrete_y
        for i in range(2,len(x)+1):
            temp = Fitting(x[:i],y[:i])
            temp.exponentialFitting1Coeff()
            
            #xForYHalved = invFunc([temp.coefficients[0],temp.coefficients[1],0],halfY)
            xForYHalved = invFunc(temp.coefficients,halfY)
            xForYHalveds.append(xForYHalved)
            
        # I know I am going to repeat the same fitting but its simpler
        self.exponentialFitting1Coeff()        
        self.setContinuousY()
        self.determineError()
        
        return xForYHalveds

#################################################
# Theoretical fitting for d1/2
#################################################
######
    def calculateTheoreticalIntensityDecay(self,beta,gamma,initialWilsonB,initialWilsonScale=1.0):
        
        
        self.log.logger.debug("CalculateTheoreticalIntensityDecay: Beta=%.2e Gamma=%.2e InitialWilsonB=%.2f"%(beta,gamma,initialWilsonB))
        
        
        # vars
#        initialWilsonB=5.0
#        beta =  0.8E-6
#        gama =0.01E-6
#        resolution = 2.5
        self.beta = beta
        self.gamma = gamma
        
        
        # values for dose 0
        idealWilsonDistributionH2 = [0.0090, 0.0131, 0.0172,0.0213, 0.0254, 0.0295,0.0335, 0.0376, 0.0417,0.0458, 0.0499, 0.0540,0.0581, 0.0622, 0.0663,0.0704, 0.0745, 0.0786,0.0826, 0.0867, 0.0908,0.0949, 0.0990, 0.1031,0.1072, 0.1113, 0.1154,0.1195, 0.1236, 0.1277,0.1318, 0.1358, 0.1399,0.1440, 0.1481, 0.1522,0.1563, 0.1604, 0.1645,0.1686, 0.1727, 0.1768,0.1809, 0.1849, 0.1890,0.1931, 0.1972, 0.2013,0.2054, 0.2095, 0.2136,0.2177, 0.2218, 0.2259,0.2300, 0.2341, 0.2381,0.2422, 0.2463, 0.2504,0.2545, 0.2586, 0.2627,0.2668, 0.2709, 0.2750,0.2791, 0.2832, 0.2873,0.2913, 0.2954, 0.2995,0.3036, 0.3077, 0.3118,0.3159, 0.3200, 0.3241,0.3282, 0.3323, 0.3364,0.3404, 0.3445, 0.3486,0.3527, 0.3568, 0.3609,0.3650, 0.3691, 0.3732,0.3773, 0.3814, 0.3855,0.3896, 0.3936, 0.3977,0.4018, 0.4059, 0.4100,0.4141, 0.4182, 0.4223,0.4264, 0.4305, 0.4346,0.4387, 0.4428, 0.4468,0.4509, 0.4550, 0.4591,0.4632, 0.4673, 0.4714,0.4755, 0.4796, 0.4837,0.4878, 0.4919, 0.4959,0.5000, 0.5041, 0.5082,0.5123, 0.5164, 0.5205,0.5246, 0.5287, 0.5328,0.5369, 0.5410, 0.5451,0.5491, 0.5532, 0.5573,0.5614, 0.5655, 0.5696,0.5737, 0.5778, 0.5819,0.5860, 0.5901, 0.5942,0.5982, 0.6023, 0.6064,0.6105, 0.6146, 0.6187,0.6228, 0.6269, 0.6310,0.6351, 0.6392, 0.6433,0.6474, 0.6514, 0.6555,0.6596, 0.6637, 0.6678,0.6719, 0.6760, 0.6801,0.6842, 0.6883, 0.6924,0.6965, 0.7006, 0.7046,0.7087, 0.7128, 0.7169,0.7210, 0.7251, 0.7292,0.7333, 0.7374, 0.7415,0.7456, 0.7497, 0.7537,0.7578, 0.7619, 0.7660,0.7701, 0.7742, 0.7783,0.7824, 0.7865, 0.7906,0.7947, 0.7988, 0.8029,0.8069, 0.8110, 0.8151,0.8192, 0.8233, 0.8274,0.8315, 0.8356, 0.8397,0.8438, 0.8479, 0.8520,0.8561, 0.8601, 0.8642,0.8683, 0.8724, 0.8765,0.8806, 0.8847, 0.8888,0.8929, 0.8970, 0.9011,0.9052, 0.9092, 0.9133,0.9174, 0.9215, 0.9256,0.9297, 0.9338, 0.9379,0.9420, 0.9461, 0.9502,0.9543, 0.9584, 0.9624,0.9665, 0.9706, 0.9747,0.9788, 0.9829, 0.9870,0.9911, 0.9952, 0.9993,1.0034, 1.0075, 1.0115,1.0156, 1.0197, 1.0238,1.0279, 1.0320, 1.0361,1.0402, 1.0443, 1.0484,1.0525, 1.0566, 1.0607,1.0647, 1.0688, 1.0729,1.0770, 1.0811, 1.0852,1.0893, 1.0934, 1.0975,1.1016, 1.1057, 1.1098,1.1139, 1.1179, 1.1220,1.1261, 1.1302, 1.1343,1.1384, 1.1425, 1.1466,1.1507, 1.1548, 1.1589,1.1630, 1.1670, 1.1711,1.1752, 1.1793, 1.1834,1.1875, 1.1916, 1.1957,1.1998, 1.2039, 1.2080,1.2121, 1.2162, 1.2202,1.2243, 1.2284, 1.2325,1.2366,1.2407,1.2448,1.2489,1.253,1.2571,1.2612,1.2653,1.2694,1.2735,1.2776,1.2817,1.2858,1.2899,1.294,1.2981,1.3022,1.3063,1.3104,1.3145,1.3186,1.3227,1.3268,1.3309,1.335,1.3391,1.3432,1.3473,1.3514,1.3555,1.3596,1.3637,1.3678,1.3719,1.376,1.3801,1.3842,1.3883,1.3924,1.3965,1.4006,1.4047,1.4088,1.4129,1.417,1.4211,1.4252,1.4293,1.4334,1.4375,1.4416,1.4457,1.4498,1.4539,1.458,1.4621,1.4662,1.4703,1.4744,1.4785,1.4826,1.4867,1.4908,1.4949,1.499,1.5031,1.5072,1.5113,1.5154,1.5195,1.5236,1.5277,1.5318,1.5359,1.5400,1.5441,1.5482,1.5523,1.5564,1.5605,1.5646,1.5687,1.5728,1.5769,1.5810,1.5851,1.5892,1.5933,1.5974,1.6015,1.6056,1.6097,1.6138,1.6179,1.6220,1.6261,1.6302,1.6343,1.6384,1.6425,1.6466,1.6507,1.6548,1.6589,1.6630,1.6671,1.6712,1.6753,1.6794,1.6835,1.6876,1.6917,1.6958,1.6999,1.7040,1.7081,1.7122,1.7163,1.7204,1.7245,1.7286,1.7327,1.7368,1.7409,1.7450,1.7491,1.7532,1.7573,1.7614,1.7655,1.7696,1.7737,1.7778,1.7819,1.7860,1.7901,1.7942,1.7983,1.8024,1.8065,1.8106,1.8147,1.8188,1.8229,1.8270,1.8311,1.8352,1.8393,1.8434,1.8475,1.8516,1.8557,1.8598,1.8639,1.8680,1.8721,1.8762,1.8803,1.8844,1.8885,1.8926,1.8967,1.9008,1.9049,1.9090,1.9131,1.9172,1.9213,1.9254,1.9295,1.9336,1.9377,1.9418,1.9459,1.9500,1.9541,1.9582,1.9623,1.9664,1.9705,1.9746,1.9787,1.9828,1.9869,1.9910,1.9951,1.9992,2.0033,2.0074,2.0115,2.0156,2.0197,2.0238,2.0279,2.0320,2.0361,2.0402,2.0443,2.0484,2.0525,2.0566,2.0607,2.0648,2.0689,2.0730,2.0771,2.0812,2.0853,2.0894,2.0935,2.0976,2.1017,2.1058,2.1099,2.1140,2.1181,2.1222,2.1263,2.1304,2.1345,2.1386,2.1427,2.1468,2.1509,2.1550,2.1591,2.1632,2.1673,2.1714,2.1755,2.1796,2.1837,2.1878,2.1919,2.1960,2.2001,2.2042,2.2083,2.2124,2.2165,2.2206,2.2247,2.2288,2.2329,2.2370,2.2411,2.2452,2.2493,2.2534,2.2575,2.2616,2.2657,2.2698,2.2739,2.2780,2.2821,2.2862,2.2903,2.2944,2.2985,2.3026,2.3067,2.3108,2.3149,2.3190,2.3231,2.3272,2.3313,2.3354,2.3395,2.3436,2.3477,2.3518,2.3559,2.3600,2.3641,2.3682,2.3723,2.3764,2.3805,2.3846,2.3887,2.3928,2.3969,2.4010,2.4051,2.4092,2.4133,2.4174,2.4215,2.4256,2.4297,2.4338,2.4379,2.4420,2.4461,2.4502,2.4543,2.4584,2.4625,2.4666,2.4707,2.4748,2.4789,2.4830,2.4871,2.4912,2.4953,2.4994,2.5035,2.5076,2.5117,2.5158,2.5199,2.5240,2.5281,2.5322,2.5363,2.5404,2.5445,2.5486,2.5527,2.5568,2.5609,2.5650,2.5691,2.5732,2.5773,2.5814,2.5855,2.5896,2.5937,2.5978,2.6019,2.6060,2.6101,2.6142,2.6183,2.6224,2.6265,2.6306,2.6347,2.6388,2.6429,2.6470,2.6511,2.6552,2.6593,2.6634,2.6675,2.6716,2.6757,2.6798,2.6839,2.6880,2.6921,2.6962,2.7003,2.7044,2.7085,2.7126,2.7167,2.7208,2.7249,2.7290,2.7331,2.7372,2.7413,2.7454,2.7495,2.7536,2.7577,2.7618,2.7659,2.7700,2.7741,2.7782,2.7823,2.7864,2.7905,2.7946,2.7987,2.8028,2.8069,2.8110,2.8151,2.8192,2.8233,2.8274,2.8315,2.8356,2.8397,2.8438,2.8479,2.8520,2.8561,2.8602,2.8643,2.8684,2.8725]
        idealWilsonDistributionValue = [117970.000, 100512.023,  80882.992, 62948.516,  57507.758,  61357.430, 72234.063,  89858.945, 109460.930,126917.039, 137405.063, 139655.375,137483.219, 133394.875, 129394.328,125762.617, 121035.289, 116051.805,110836.078, 104613.297,  97322.055, 89836.305,  83216.188,  78146.273, 73459.672,  69471.023,  65299.645, 61581.441,  58510.613,  55865.180, 53658.789,  52101.020,  51070.418, 50092.043,  49350.723,  48151.910, 47058.906,  46675.406,  46597.676, 45924.047,  46080.672,  45937.621, 46096.023,  45896.965,  45990.094, 46123.293,  46343.516,  45936.539, 45715.695,  45109.164,  44549.133, 43634.820,  43566.086,  43451.016, 42696.293,  41173.980,  39972.754, 39166.629,  38020.367,  36810.992, 35497.309,  34194.906,  32992.742, 31585.996,  30211.492,  29119.816, 28151.564,  27386.414,  26232.775, 25235.693,  24318.244,  23707.949, 22821.910,  22182.096,  21694.740, 21236.889,  20733.123,  20323.289, 20073.404,  19932.156,  19631.480, 19223.189,  18920.273,  18557.662, 18134.789,  17926.918,  17909.145, 17908.371,  17781.652,  17634.252, 17607.758,  17273.971,  17132.121, 16953.238,  16883.561,  16615.092, 16435.377,  16423.141,  16351.833, 16278.806,  15998.301,  15795.754, 15589.186,  15561.384,  15467.072, 15476.589,  15331.998,  15028.964, 14745.987,  14509.142,  14445.926, 14254.643,  14111.921,  13900.479, 13785.526,  13686.093,  13464.846, 13304.157,  13084.093,  13114.881, 13089.596,  13244.095,  13117.398, 13140.626,  13031.727,  12999.481, 12835.458,  12954.440,  12937.747, 12936.304,  12825.827,  12995.077, 12994.031,  13036.257,  13006.766, 13057.586,  13010.016,  12891.707, 12966.081,  13114.423,  13119.474, 13065.754,  13052.747,  13214.619, 13376.885,  13386.037,  13244.184, 13225.625,  13203.178,  13157.919, 13058.345,  13089.547,  13236.270, 13356.928,  13294.085,  13322.506, 13356.878,  13574.700,  13741.788, 13988.013,  14126.934,  14226.778, 14096.913,  14083.928,  14170.343, 14351.646,  14494.585,  14485.082, 14514.434,  14622.690,  14725.597, 14840.912,  14869.137,  14947.929, 15039.328,  15069.899,  15058.230, 14892.115,  14829.184,  14854.609, 14911.043,  14950.722,  15113.783, 15211.773,  15205.695,  15024.023, 14926.859,  14948.205,  14968.500, 14961.653,  14880.744,  14853.396, 14715.400,  14625.747,  14476.197, 14315.362,  14115.836,  14177.435, 14214.169,  13756.128,  13478.938, 13409.521,  13313.305,  13191.076, 13068.228,  13143.240,  13034.021, 12844.786,  12565.626,  12494.126, 12431.333,  12224.259,  12045.229, 11934.917,  11999.310,  12092.722, 12073.927,  12000.386,  11492.284, 11340.666,  11261.278,  11170.411, 11033.554,  10920.556,  10805.261, 10749.542,  10633.937,  10553.671, 10396.852,  10345.898,  10439.532, 10444.084,  10338.728,  10137.357, 10024.374,   9960.443,   9843.068,  9813.853,   9774.964,   9722.901,  9668.755,   9489.759,   9437.470,  9337.847,   9232.355,   9143.001,  8946.202,   9061.576,   8927.707,  8833.817,   8559.503,   8737.791,  8741.253,   8734.717,   8730.013,  8553.071,   8567.203,   8448.906,  8348.450,   8372.744,   8420.621,  8534.404,   8515.739,   8391.372,  8376.129,   8364.006,   8370.607,  8053.081,   7885.547,   7949.570,  8098.683,   8009.885,   7884.853,  7912.111,   7977.090,   8038.597,  7984.881,   7943.616,   8002.785,  7840.147,   7771.715,   7704.840,  7606.398,   7499.033,   7380.200,  7353.043,   7373.826,   7386.296,  7445.311,   7298.761,   7163.549,6936.293,6920.410,6888.470,7020.130,   6991.486,6970.270,6894.089,6915.407,6934.171,6726.973509,6686.434089,6646.138977,6606.086698,6566.275791,6526.704799,6487.372279,6448.276792,6409.416909,6370.791212,6332.398289,6294.236737,6256.305161,6218.602176,6181.126405,6143.876477,6106.851032,6070.048718,6033.468188,5997.108108,5960.967148,5925.043987,5889.337314,5853.845824,5818.568219,5783.503211,5748.649519,5714.005869,5679.570996,5645.343641,5611.322553,5577.506491,5543.894217,5510.484504,5477.276131,5444.267885,5411.45856,5378.846957,5346.431885,5314.212159,5282.186601,5250.354043,5218.71332,5187.263276,5156.002763,5124.930639,5094.045767,5063.34702,5032.833276,5002.503419,4972.356343,4942.390945,4912.60613,4883.00081,4853.573904,4824.324336,4795.251038,4766.352947,4737.629007,4709.078169,4680.69939,4652.491632,4624.453866,4596.585067,4568.884216,4541.350301,4513.982317,4486.779263,4459.740146,4432.863977,4406.149774,4379.596562,4353.20337,4326.969234,4300.893196,4274.974301,4249.211605,4223.604165,4198.151045,4172.851316,4147.704053,4122.708338,4097.863257,4073.167902,4048.621371,4024.222768,3999.9712,3975.865781,3951.905632,3928.089876,3904.417643,3880.888068,3857.500292,3834.25346,3811.146723,3788.179236,3765.35016,3742.658662,3720.103911,3697.685085,3675.401363,3653.251931,3631.235981,3609.352708,3587.601312,3565.980999,3544.490978,3523.130465,3501.898679,3480.794844,3459.818189,3438.967947,3418.243358,3397.643663,3377.16811,3356.815951,3336.586442,3316.478844,3296.492423,3276.626448,3256.880193,3237.252936,3217.743962,3198.352556,3179.078011,3159.919621,3140.876688,3121.948515,3103.134411,3084.433688,3065.845663,3047.369657,3029.004995,3010.751005,2992.607021,2974.57238,2956.646424,2938.828495,2921.117945,2903.514126,2886.016394,2868.624111,2851.336641,2834.153351,2817.073615,2800.096808,2783.222311,2766.449505,2749.77778,2733.206524,2716.735134,2700.363007,2684.089545,2667.914153,2651.836241,2635.85522,2619.970507,2604.181522,2588.487688,2572.888431,2557.383182,2541.971373,2526.652442,2511.425828,2496.290977,2481.247334,2466.29435,2451.431479,2436.658177,2421.973905,2407.378127,2392.870308,2378.449919,2364.116433,2349.869327,2335.708079,2321.632173,2307.641093,2293.73433,2279.911374,2266.17172,2252.514868,2238.940317,2225.447571,2212.036139,2198.705528,2185.455254,2172.284831,2159.193778,2146.181617,2133.247872,2120.392072,2107.613745,2094.912426,2082.28765,2069.738956,2057.265885,2044.867982,2032.544794,2020.29587,2008.120763,1996.019028,1983.990223,1972.033909,1960.149647,1948.337005,1936.595551,1924.924856,1913.324493,1901.794038,1890.33307,1878.941171,1867.617923,1856.362914,1845.175733,1834.055969,1823.003218,1812.017075,1801.097139,1790.243011,1779.454294,1768.730594,1758.07152,1747.476681,1736.945691,1726.478165,1716.073721,1705.731978,1695.452558,1685.235086,1675.079189,1664.984495,1654.950636,1644.977245,1635.063957,1625.210411,1615.416246,1605.681105,1596.004632,1586.386472,1576.826276,1567.323694,1557.878377,1548.489982,1539.158165,1529.882586,1520.662904,1511.498784,1502.389891,1493.335892,1484.336455,1475.391253,1466.499958,1457.662246,1448.877793,1440.146279,1431.467384,1422.840792,1414.266187,1405.743256,1397.271688,1388.851173,1380.481403,1372.162073,1363.892878,1355.673517,1347.503688,1339.383095,1331.311439,1323.288427,1315.313764,1307.38716,1299.508325,1291.67697,1283.892811,1276.155562,1268.46494,1260.820666,1253.222459,1245.670041,1238.163138,1230.701474,1223.284777,1215.912776,1208.585202,1201.301787,1194.062264,1186.86637,1179.713841,1172.604415,1165.537835,1158.51384,1151.532174,1144.592583,1137.694813,1130.838611,1124.023727,1117.249913,1110.51692,1103.824504,1097.172418,1090.56042,1083.988269,1077.455724,1070.962547,1064.508501,1058.093349,1051.716857,1045.378793,1039.078924,1032.817021,1026.592855,1020.406198,1014.256824,1008.144509,1002.069029,996.0301617,990.0276876,984.0613867,978.1310412,972.2364343,966.3773506,960.5535761,954.7648979,949.0111047,943.2919861,937.6073332,931.9569382,926.3405948,920.7580977,915.209243,909.6938279,904.2116508,898.7625116,893.346211,887.9625512,882.6113354,877.2923683,872.0054553,866.7504034,861.5270205,856.3351158,851.1744996,846.0449833,840.9463796,835.878502,830.8411655,825.834186,820.8573805,815.9105673,810.9935655,806.1061955,801.2482787,796.4196377,791.620096,786.8494783,782.1076102,777.3943185,772.7094309,768.0527764,763.4241847,758.8234867,754.2505144,749.7051006,745.1870793,740.6962854,736.2325548,731.7957244,727.3856321,723.0021168,718.6450183,714.3141775,710.0094359,705.7306365,701.4776228,697.2502395,693.0483321,688.871747,684.7203317,680.5939345,676.4924046,672.4155921,668.3633481,664.3355246,660.3319743,656.3525511,652.3971094,648.4655048,644.5575936,640.673233,636.8122811,632.9745969,629.16004,625.3684712,621.5997519,617.8537445,614.1303119,610.4293182,606.7506282,603.0941075]
        
        self.idealWilsonDistributionH2 = np.array(idealWilsonDistributionH2)
        self.idealWilsonDistributionValue = np.array(idealWilsonDistributionValue)
        
        self.idealWilsonDistributionResolution =  np.sqrt(1./self.idealWilsonDistributionH2) # R = 1/H^2
        

        idealWilsonDistributionLength=len(idealWilsonDistributionH2)
        idealWilsonDistributionDeltaH2=(idealWilsonDistributionH2[idealWilsonDistributionLength-1]-\
                                        idealWilsonDistributionH2[0])/(idealWilsonDistributionLength-1) # step
        idealWilsonDistributionDeltaH=np.sqrt(idealWilsonDistributionDeltaH2)
        

        # for this initial scale and B factor
        self.i0PerBin = idealWilsonDistributionValue * \
        np.exp(-initialWilsonB*self.idealWilsonDistributionH2/2.)*initialWilsonScale*4*np.pi*self.idealWilsonDistributionH2*idealWilsonDistributionDeltaH
            
        # from low resolution to high
        self.i0AccumulatedPerBin = np.add.accumulate(self.i0PerBin)
                
        # need to optimise from here on
        
    def doTheoreticalIntensityDecayCurve(self,resolution):
        
        self.log.logger.debug("Getting the Theoretical Intensity Decay Curve up to %.2f A"%(resolution))
        
        self.resolutionLimitIndex = len(self.idealWilsonDistributionResolution)-1
        for idx,i in enumerate(self.idealWilsonDistributionResolution) :
            if i < resolution :
                self.resolutionLimitIndex = idx
                break
        
        doseRange = self.continuous_x
        
        iOverI0 = []
        for dose in doseRange :
            intensityPerBin = self.i0PerBin*np.exp(-self.beta*dose*self.idealWilsonDistributionH2/2.)*np.exp(-(self.gamma*dose)**2)
            intensityAccumulatedPerBin = np.add.accumulate(intensityPerBin)
            
            iOverI0.append(intensityAccumulatedPerBin[self.resolutionLimitIndex]/self.i0AccumulatedPerBin[self.resolutionLimitIndex])
            #print '%.3e %1.3f'%(dose,iOverI0[-1])
        
        self.continuous_y = iOverI0
        self.function = self.funcTheoreticalIntensityDecay
    
    def funcTheoreticalIntensityDecay(self,coeffs,x):
        
        iOverI0 = []
        for dose in x :
            intensityPerBin = self.i0PerBin*np.exp(-self.beta*dose*self.idealWilsonDistributionH2/2.)*np.exp(-(self.gamma*dose)**2)
            intensityAccumulatedPerBin = np.add.accumulate(intensityPerBin)
            
            iOverI0.append(intensityAccumulatedPerBin[self.resolutionLimitIndex]/self.i0AccumulatedPerBin[self.resolutionLimitIndex])
            #print '%.3e %1.3f'%(dose,iOverI0[-1])
        
        return np.array(iOverI0)
    
    
    def getTheoreticalDOneHalf(self):
        
        
        def interpolateXFromY(x0,x1,y0,y1,y):
            return x0 + ( (x1-x0)*(y-y0) / (y1-y0) )
        
        for i,v in enumerate(self.continuous_y) :
            if v < 0.5 :
                break
        
        d = interpolateXFromY(self.continuous_x[i-1],self.continuous_x[i],self.continuous_y[i-1],self.continuous_y[i],0.5)
        
        self.log.logger.debug('Theoretical Interpolated Dose 1/2 = %.2e Gy'% d)
        
        return d
      
#        dd=endDose/numberOfPoints
#        dose=-dd
#                
#        
#        jh=0
#        
#        doseRange=[]
#        
#        iOverI0 = []
#        for k in range(numberOfPoints) :
#            sumIntensity = []
#            dose=dose+dd
#            doseRange.append(dose)
#            
#            s_drop=np.exp(-(self.gamma*dose)**2)
#            sumIntensity.append(self.i0PerBin[0]*np.exp(-self.beta*dose*self.idealWilsonDistributionH2[0]/2)*s_drop)
#            
#            for j in range(1,resolutionLimitIndex) :
#                drop=np.exp(-self.beta*dose*self.idealWilsonDistributionH2[j]/2.)*s_drop
#                sumIntensity.append(sumIntensity[j-1]+self.i0PerBin[j]*drop)
#            
#            
#            iOverI0.append(sumIntensity[resolutionLimitIndex-1]/self.i0AccumulatedPerBin[resolutionLimitIndex-1])
#            
#            print '%.3e %1.3f'%(doseRange[k],iOverI0[k])#,sumIntensity[resolutionLimitIndex-1],i0AccumulatedPerBin[resolutionLimitIndex-1]
#      
#            if iOverI0[k] >= 0.4999999:
#                jh=k
#            
#            
#        print 'Res_dose1/2 = ',doseRange[jh],iOverI0[jh]
        
#        import matplotlib.pyplot as plt
#        plt.plot(doseRange,iOverI0)
#        #plt.plot(iOverI0,doseRange)
#        plt.show()    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        

    
    
    
###############################################################################
# TESTS
###########################
    
def testLinear():
    ##########
    # Generate data points with noise
    ##########
    num_points = 10
    func = lambda x: 10+ x
    
    # Note: all positive, non-zero data
    xdata = np.linspace(10.1, 110.1, num_points)
    ydata = func(xdata)     # simulated perfect data
    yerr = 0.2 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr       # simulated noisy data
    
    #####
    
    
    fit = Fitting(xdata,ydata)
    fit.setContinuousX()
    fit.linearFitting2Coeffs()
    fit.determineError()
    fit.setContinuousY()
    
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()

def testLinear1Coeff():
    ##########
    # Generate data points with noise
    ##########
    num_points = 10
    func = lambda x: 10+ x
    
    # Note: all positive, non-zero data
    xdata = np.linspace(10.1, 110.1, num_points)
    ydata = func(xdata)     # simulated perfect data
    yerr = 0.2 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr       # simulated noisy data
    
    #####
    
    
    fit = Fitting(xdata,ydata)
    fit.setContinuousX()
    fit.linearFitting1Coeff()
    fit.determineError()
    fit.setContinuousY()
    
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()
def testMulipleLinear():
    ##########
    # Generate data points with noise
    ##########
    num_points = 10
    func = lambda x: 2 + x
    
    # Note: all positive, non-zero data
    xdata = np.linspace(10.1, 110.1, num_points)
    ydata = func(xdata)     # simulated perfect data
    yerr = 0.2 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr       # simulated noisy data
    
    #####
    
    
    fit = Fitting(xdata,ydata)
    slopes = fit.doMultipleLinearFitting1Coeff()
    
    print 'Slopes of all data:', ['%.2f'%s for s in slopes]
    print 'Last slope: %.2f'%fit.coefficients[0]
    
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()
    
    
def testMulipleExponentialReturnHalved():
    
    realAccumulatedDose=[8078.43137255,
    24836.6013072,
    41594.7712418,
    58352.9411765,
    75111.1111111,
    108627.45098,
    125385.620915,
    142143.79085,
    158901.960784]
    
    relativeAverageIntegratedIntensity=[1,
    0.9959506111,
    0.9148125122,
    0.8668467836,
    0.7912513356,
    0.7108194479,
    0.6382561881,
    0.5988188326,
    0.5796369558]
    
    xdata = np.array(realAccumulatedDose)
    ydata = np.array(relativeAverageIntegratedIntensity)
    
    fit = Fitting(xdata,ydata)
    xForYHalved = fit.doMultipleExponentialFittingReturnHalfY()
    
    print 'X values for Y halved:', ['%.2e'%s for s in xForYHalved]
    
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()

    
    
def testExponential():
    ##########
    # Generate data points with noise
    ##########
    num_points = 10
    func = lambda x: np.exp(x)
    
    # Note: all positive, non-zero data
    xdata = np.linspace(0.1, 9.1, num_points)
    ydata = func(xdata)     # simulated perfect data
    yerr = 0.2 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr       # simulated noisy data
    
    #####
    
    
    fit = Fitting(xdata,ydata)
    fit.setContinuousX()
    fit.exponentialFitting3Coeffs()
    fit.determineError()
    fit.setContinuousY()
   
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()

def testExponentialNegative():
    ##########
    # Generate data points with noise
    ##########
    num_points = 20
    func = lambda x: np.exp(-x)
    
    # Note: all positive, non-zero data
    xdata = np.linspace(0.01,1,  num_points)
    ydata = func(xdata)     # simulated perfect data
    yerr = 0.02 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr       # simulated noisy data
    
    #####
    
    
    fit = Fitting(xdata,ydata)
    fit.setContinuousX()
    fit.exponentialFitting3Coeffs()
    fit.determineError()
    fit.setContinuousY()
   
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()

def testTheoreticalDOneHalf():
    
    # data from:
    # /mntdirect/_data_id23eh1_inhouse/opid231/20110515/PROCESSED_DATA/INS_I23_ROOM
    # in1.csv
    realAccumulatedDose=[8078.43137255,  
    24836.6013072,  
    41594.7712418,  
    58352.9411765,  
    75111.1111111,  
    108627.45098,   
    125385.620915,  
    142143.79085,   
    158901.960784]
    
    # relativeAverageIntegratedIntensity_0.00
    relativeAverageIntegratedIntensity=[1.0,                                    
    0.995950611132,                         
    0.914812512202,                         
    0.866846783642,                         
    0.79125133555,                           
    0.710819447918,                         
    0.638256188113,                         
    0.598818832578,                         
    0.579636955783]                         

    
    xdata = np.array(realAccumulatedDose)
    ydata = np.array(relativeAverageIntegratedIntensity)
    
    
    fit = Fitting(xdata,ydata)
    fit.setContinuousX()
    fit.calculateTheoreticalIntensityDecay(beta=3.79846997934e-05,gamma = 3.90990650196e-06,initialWilsonB=17.5)
    fit.doTheoreticalIntensityDecayCurve(resolution=2.5)
    d = fit.getTheoreticalDOneHalf()
    print d
    
    import matplotlib.pyplot as plt
    plt.plot(fit.discrete_x, fit.discrete_y,marker='o',linewidth=0,markeredgecolor='blue', markerfacecolor='None')
    plt.plot(fit.continuous_x, fit.continuous_y)
    plt.show()
    
    
            # Dose 1/2
#    b.calculateTheoreticalIntensityDecay(beta=  0.8E-6,gamma = 0.01E-6,initialWilsonB=5.0)
#    b.getTheoreticalIntensityDecayCurve(resolution=2.5,endDose=50e6)
#    import matplotlib.pyplot as plt
#    plt.plot(b.doseRange,b.iOverI0)
#    plt.show()
#    b.getTheoreticalDOneHalf()


if __name__ == "__main__":
    
    
    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)
    
    #testLinear()
    #testLinear1Coeff()
    #testMulipleLinear()
    #testExponentialNegative()
    #testMulipleExponentialReturnHalved()
    
    testTheoreticalDOneHalf()



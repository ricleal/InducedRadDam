'''
Created on 31 May 2011

@author: leal
'''

import matplotlib
# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.ticker import OldScalarFormatter
import numpy as np
import scipy.optimize as opt
import pylab as pl
import sys
import localLogger
import pprint
import os


class Plot(object):
    '''
    classdocs
    '''

    #===========================================================================
    #  Constructor
    #===========================================================================
    
    def __init__(self):
        '''
        Constructor
        
        '''
        self.log = localLogger.LocalLogger("plot")
        
    #===========================================================================
    # Private Methods 
    #===========================================================================

    
    #===========================================================================
    #  Public methods
    #===========================================================================
    
    def createPlot(self, title):
        '''
        Creates a window for a plot
        Optional. You can call plot without this.
        '''
        self.title = title
        self.fig = plt.figure()
        self.fig.canvas.set_window_title(title)
        self.ax = self.fig.add_subplot(111)
    
    
    def createPlotDoubleYAxis(self, title):
        '''
        Creates a window for a plot
        Optional. You can call plot without this.
        '''
        self.title = title
        self.fig = plt.figure(figsize=(9,9), dpi=80)
        #self.fig.suptitle(title)
        self.fig.canvas.set_window_title(title)
        self.ax = self.fig.add_subplot(111)
        pl.subplots_adjust(bottom=0.2)
        self.ax2 = self.ax.twinx()
        self.ax.grid(True)


    
    def plotDiscreteValues(self,xField,yField,axis=None,marker='o',color='blue',label=""):
        """
        Plot values 
        """
        if axis is None:
            axis = self.ax
        
#        self.log.logger.debug('X'+str(xField))
#        self.log.logger.debug('Y'+str(yField))
        
        axis.plot(xField,yField,marker=marker,linewidth=0,markeredgecolor=color, markerfacecolor='None', label=label)


    def plotContinuousValues(self,xField,yField,axis=None,color='blue',label=""):
        """
        Plot values 
        """
        if axis is None:
            axis = self.ax
        
        axis.plot(xField, yField, linestyle='solid',color=color, linewidth=1,label=label)
    
    
    def setAxisTitles(self,x,y1,y2=None,textFontSize = 12):
    
        matplotlib.rc('text', usetex=True)
        matplotlib.rc('font', family='serif')
        matplotlib.rc('font', weight='bold')
          
        self.ax.set_xlabel(x, fontsize=textFontSize)
        self.ax.set_ylabel(y1, fontsize=textFontSize)
        if y2 is not None:
            self.ax2.set_ylabel(y2, fontsize=textFontSize)
            
        matplotlib.rcdefaults()
    
    def setBottomText(self,text,textFontSize = 16):
        
        matplotlib.rc('text', usetex=True)
        matplotlib.rc('font', family='serif')
        matplotlib.rc('font', weight='bold')
          
        # Add beta + delta text to the plot        
        self.ax.text(0.5, 0.03,text, fontsize=textFontSize,
                     horizontalalignment='center', verticalalignment='center', transform = self.ax.transAxes,
                     bbox=dict(facecolor='grey', alpha=0.1,boxstyle='round'))
        
            
        matplotlib.rcdefaults()
    
    
    
    @staticmethod
    def show(onlyDraw=False):
        """
        Show all plots created
        """
        if onlyDraw is True:
            # Doesn't open a window!!
            plt.draw()
        else:
            plt.show()
            


        

        
        
        
    
    def savePlot(self,filePath):
        pngFileName = filePath + os.extsep + 'png'
        svgFileName = filePath + os.extsep + 'svg'
        

        # Now check everything with the defaults:
#        dpi = self.fig.get_dpi()
#        print "DPI:", dpi
#        defaultSize = self.fig.get_size_inches()
#        print "Default size in Inches", defaultSize
#        print "Which should result in a %i x %i Image"%(dpi*defaultSize[0], dpi*defaultSize[1])
#        # the default is 100dpi for savefig:
#        self.fig.savefig("test1.png")
#        # this gives me a 797 x 566 pixel image, which is about 100 DPI
#        
#        # Now make the image twice as big, while keeping the fonts and all the
#        # same size
#        self.fig.set_size_inches( (defaultSize[0]*2, defaultSize[1]*2) )
#        size = self.fig.get_size_inches()
#        print "Size in Inches", size
#        self.fig.savefig("test2.png")
#        # this results in a 1595x1132 image
#        
#        # Now make the image twice as big, making all the fonts and lines
#        # bigger too.
        
#        self.fig.set_size_inches( defaultSize )# resetthe size
#        size = self.fig.get_size_inches()
#        print "Size in Inches", size
#        self.fig.savefig("test3.png", dpi = (200)) # change the dpi
#        # this also results in a 1595x1132 image, but the fonts are larger.
        
        self.log.logger.info('Saving: ' + svgFileName)
        self.fig.savefig(svgFileName, dpi=(200))
        self.log.logger.info('Saving: ' + pngFileName)
        self.fig.savefig(pngFileName, dpi=(200))


 
        
    
        
    def addLegend(self, textFontSize = 12):

        #leg=self.ax.legend(loc='lower right')
        leg=self.ax.legend(loc=(0.65,-0.2),frameon=False)
        for t in leg.get_texts():
            t.set_fontsize(textFontSize)    # the legend text fontsize

        #leg2=ax2.legend(loc='lower left')
        leg2=self.ax2.legend(loc=(0.0,-0.2),frameon=False)
        for t in leg2.get_texts():
            t.set_fontsize(textFontSize)    # the legend text fontsize
        
        self.ax.xaxis.set_major_formatter(OldScalarFormatter())
        # xtikcs
#        locs,labels = plt.xticks()
#        plt.xticks(locs, map(lambda x: "%.1e" % x, locs))

    

if __name__ == "__main__":
    
    
    # Need this to initialise!
    import ini
    configIniFileName = 'config.ini'
    ini.Ini(configIniFileName)
    
    import fitting
    
    
    #testLinear()
    ##########
    # Generate data points with noise
    ##########
    num_points = 10
    func = lambda x: -1+x
    
    # Note: all positive, non-zero data
    xdata = np.linspace(0.1, 2, num_points)
    ydata = func(xdata)     # simulated perfect data
    #print ydata
    yerr = 0.1 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr       # simulated noisy data
    #print ydata
    #####
    
    
    fitLinear = fitting.Fitting(xdata,ydata)
    fitLinear.setContinuousX()
    fitLinear.linearFitting2Coeffs()
    fitLinear.determineError()
    fitLinear.setContinuousY()
    
    

    
    plot1 = Plot()
    plot1.createPlotDoubleYAxis("Test Plot")
    plot1.plotDiscreteValues(fitLinear.discrete_x, fitLinear.discrete_y, 
                                     plot1.ax, 'o', 'blue', 'Overall B-factor')
    plot1.plotContinuousValues(fitLinear.continuous_x, fitLinear.continuous_y,
                                       plot1.ax, 'blue')
   
   
    
    #testExponential
    ##########
    # Generate data points with noise
    ##########
    num_points = 20
    funce = lambda x: np.exp(-x)
    
    # Note: all positive, non-zero data
    xdata = np.linspace(0.1, 2, num_points)
    ydata = funce(xdata)     # simulated perfect data
    yerr = 0.05 * ydata                      # simulated errors (10%)
    ydata += np.random.randn(num_points) * yerr     # simulated noisy data
    
    #####
    
    
    fitExp = fitting.Fitting(xdata,ydata)
    fitExp.setContinuousX()
    fitExp.exponentialFitting3Coeffs()
    fitExp.determineError()
    fitExp.setContinuousY()
    
    
    
    
    plot1.plotDiscreteValues(fitExp.discrete_x, fitExp.discrete_y, 
                             plot1.ax2, '*', 'green', 'Relative average integrated intensity')
    plot1.plotContinuousValues(fitExp.continuous_x, fitExp.continuous_y,
                               plot1.ax2, 'green')
    
    plot1.setAxisTitles('Dose (Gy)','B-Factor ($\\AA^2$)','Relative Scale')
    
    bottomText= '$\\alpha = %.2e$ : $\\beta = %.2e$ ' \
        %(fitLinear.coefficients[0],fitExp.coefficients[1])
    plot1.setBottomText(bottomText)
    plot1.addLegend()
    plot1.savePlot('/tmp/testplot')
    Plot.show()


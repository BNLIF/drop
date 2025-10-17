import numpy as np
from scipy.stats import chi2
import pandas as pd
import os
from ast import literal_eval

class whereIsEverything:
    def __init__(self,path,detector,date):
        self.detector=detector
        self.date=self.convertDate(date)
        columns=pd.MultiIndex.from_product([['hasData','dataLocation','phase','numFiles','hasCSV','CSVLocation','CSVValidated'],["1t","30t"]])
        converters={column:literal_eval for column in columns}
        self.df=pd.read_csv(path,index_col=0,header=[0,1],parse_dates=True,converters=converters)
        self.dfRow=self.df.loc[self.date]
        self.dateString=self.date.strftime("%y%m%d")
        
    def convertDate(self,date):
        if type(date)==pd.Timestamp:
            return date
        else:
            return pd.to_datetime(date,format="%y%m%d")
    
    def where(self):
        return self.dfRow["dataLocation",self.detector]
    
    def phase(self):
        return self.dfRow["phase",self.detector]
    
    def summary(self):
        if self.dfRow["hasData",self.detector]:
            for n,loc in enumerate(self.dfRow["dataLocation",self.detector]):
                nF=self.dfRow["numFiles",self.detector][n]
                print("{} data file(s) in {}".format(nF,loc))
        else:
            print("there is no data on this date in this detector")
        if self.dfRow["CSVValidated",self.detector]:
            for n,val in enumerate(self.dfRow["CSVValidated",self.detector]):
                if val:
                    print("validated calibration file in {}".format(self.dfRow["CSVLocation",self.detector][n]))
                else:
                    print("unvalidated calibration file in {}".format(self.dfRow["CSVLocation",self.detector][n]))
        else:
            print("there is no calibration file on this date in this detector")
        
    def hasData(self):
        return self.dfRow["hasData",self.detector]
    
    def bestCSV(self,allowFuture=True,maxDiff=31):
        diff=0
        while diff<maxDiff:
            currentDate=self.date-pd.Timedelta(diff,"day")
            dateString=currentDate.strftime("%y%m%d")
            csvValList=self.df.loc[currentDate,("CSVValidated",self.detector)]
            if csvValList:
                csvLocList=np.array(self.df.loc[currentDate,("CSVLocation",self.detector)])
                if True in csvValList:
                    return [os.path.join(dir,file) for dir in csvLocList[csvValList] for file in os.listdir(dir) if dateString in file]
                    
                else:
                    return [os.path.join(dir,file) for dir in csvLocList for file in os.listdir(dir) if dateString in file]
            if allowFuture:
                currentDate=self.date+pd.Timedelta(diff,"day")
                dateString=currentDate.strftime("%y%m%d")
                csvValList=self.df.loc[currentDate,("CSVValidated",self.detector)]
                if csvValList:
                    csvLocList=np.array(self.df.loc[currentDate,("CSVLocation",self.detector)])
                    if True in csvValList:
                        return [os.path.join(dir,file) for dir in csvLocList[csvValList] for file in os.listdir(dir) if dateString in file]
                        
                    else:
                        return [os.path.join(dir,file) for dir in csvLocList for file in os.listdir(dir) if dateString in file]
            diff+=1
        print("no nearby calibration files (try increasing maxDiff?)")
        return []
    
    def iterAll(self):
        allFiles=[os.path.join(dir,file) for dir in self.where() for file in os.listdir(dir) if self.dateString in file]
        for n in range(len(allFiles)):
            yield allFiles[n]
        
    def iterLoc(self,dir):
        someFiles=[os.path.join(dir,file) for file in os.listdir(dir) if self.dateString in file]
        for n in range(len(someFiles)):
            yield someFiles[n]
            
    def iterMost(self):
        dir=self.where()[np.argmax(self.dfRow["numFiles",self.detector])]
        mostFiles=[os.path.join(dir,file) for file in os.listdir(dir) if self.dateString in file]
        for n in range(len(mostFiles)):
            yield mostFiles[n]
    


def calc_chi2(func, xdata, ydata, popt):
    y = func(xdata, popt[0], popt[1], popt[2])
    r = (y-ydata)/np.sqrt(ydata)
    r2 = np.square(r)
    return np.sum(r2)

def calc1SigmaGaussianMeanError(xdata,ydata,popt,steps=15):
    muOpt=popt[0]

    deltachi2=chi2.ppf(1-.683,len(xdata)-3)

    chi2Opt=calc_chi2(gauss,xdata,ydata,popt)
    
    #find negative error
    iterationDepthLimit=steps
    upperBound=muOpt
    lowerBound=xdata[0]
    muErrNeg=(lowerBound+upperBound)/2
    chi2Err=calc_chi2(gauss,xdata,ydata,[muErrNeg,popt[1],popt[2]])
    while iterationDepthLimit and abs(chi2Err-chi2Opt)>0.001:
        if chi2Err-chi2Opt>deltachi2:
            lowerBound=muErrNeg
        if chi2Err-chi2Opt<deltachi2:
            upperBound=muErrNeg
        muErrNeg=(lowerBound+upperBound)/2
        chi2Err=calc_chi2(gauss,xdata,ydata,[muErrNeg,popt[1],popt[2]])
        iterationDepthLimit-=1
    errNeg=muOpt-muErrNeg

    #find positive error
    iterationDepthLimit=steps
    upperBound=xdata[-1]
    lowerBound=muOpt
    muErrPos=(lowerBound+upperBound)/2
    chi2Err=calc_chi2(gauss,xdata,ydata,[muErrPos,popt[1],popt[2]])
    while iterationDepthLimit and abs(chi2Err-chi2Opt)>0.001:
        if chi2Err-chi2Opt>deltachi2:
            upperBound=muErrPos
        if chi2Err-chi2Opt<deltachi2:
            lowerBound=muErrPos
        muErrPos=(lowerBound+upperBound)/2
        chi2Err=calc_chi2(gauss,xdata,ydata,[muErrPos,popt[1],popt[2]])
        iterationDepthLimit-=1
    errPos=muErrPos-muOpt

    return [errNeg,errPos]

def calc1SigmaGaussianWidthError(xdata,ydata,popt,steps=15):
    sigmaOpt=popt[1]

    deltachi2=chi2.ppf(1-.683,len(xdata)-3)

    chi2Opt=calc_chi2(gauss,xdata,ydata,popt)
    
    #find negative error
    iterationDepthLimit=steps
    upperBound=sigmaOpt
    lowerBound=0
    sigmaErrNeg=(lowerBound+upperBound)/2
    chi2Err=calc_chi2(gauss,xdata,ydata,[popt[0],sigmaErrNeg,popt[2]])
    while iterationDepthLimit and abs(chi2Err-chi2Opt)>0.001:
        if chi2Err-chi2Opt>deltachi2:
            lowerBound=sigmaErrNeg
        if chi2Err-chi2Opt<deltachi2:
            upperBound=sigmaErrNeg
        sigmaErrNeg=(lowerBound+upperBound)/2
        chi2Err=calc_chi2(gauss,xdata,ydata,[popt[0],sigmaErrNeg,popt[2]])
        iterationDepthLimit-=1
    errNeg=sigmaOpt-sigmaErrNeg

    #find positive error
    iterationDepthLimit=steps
    upperBound=2*sigmaOpt
    lowerBound=sigmaOpt
    sigmaErrPos=(lowerBound+upperBound)/2
    chi2Err=calc_chi2(gauss,xdata,ydata,[popt[0],sigmaErrPos,popt[2]])
    while iterationDepthLimit and abs(chi2Err-chi2Opt)>0.001:
        if chi2Err-chi2Opt>deltachi2:
            upperBound=sigmaErrPos
        if chi2Err-chi2Opt<deltachi2:
            lowerBound=sigmaErrPos
        sigmaErrPos=(lowerBound+upperBound)/2
        chi2Err=calc_chi2(gauss,xdata,ydata,[popt[0],sigmaErrPos,popt[2]])
        iterationDepthLimit-=1
    errPos=sigmaErrPos-sigmaOpt

    return [errNeg,errPos]

def gauss(x, mu, sigma,scale):
    arg = (x-mu)/sigma
    N = scale/np.sqrt(2*np.pi)/sigma
    return N*np.exp(-0.5*arg*arg)

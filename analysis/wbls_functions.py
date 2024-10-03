import numpy as np
from scipy.stats import chi2



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

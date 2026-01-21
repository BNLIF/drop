#get a list of the files we're going to use


import sys
from datetime import datetime
import os

directory='/media/disk_a/WbLS-DATA/raw_root/phase6/muon/'
date=sys.argv[1]
dateString=datetime.strptime(date,'%y%m%d').strftime('%d %b %Y')
allRootFiles=os.listdir(directory)
inFiles=list(filter(lambda file: date in file,allRootFiles))

if not inFiles:
    directory='/media/disk_a/WbLS-DATA/raw_root/phase7/muon/'
    allRootFiles=os.listdir(directory)
    inFiles=list(filter(lambda file: date in file,allRootFiles))
    if not inFiles:
        print('no root files found for date {}'.format(dateString))
        exit(0)


#root files are too big to hold in memory all at the same time
#loop over files, process, and build up the histograms file by file

        
import re
from wbls_vars import *
from wbls_functions import *
import uproot
import math
import numpy as np



def findRoi(eventMaximumTimes,peakMask=None,roiLength=40):
    density=[]
    for v in range(int(np.max(eventMaximumTimes[peakMask]))):
        ins=np.sum([v<time<v+roiLength for time in eventMaximumTimes[peakMask]])
        density.append(ins)
    roiStart=int(density.index(max(density)))
    return (roiStart,roiStart+roiLength)

voltageFactor=2000/(pow(2,14)-1)

speHistograms={}
speHistogramsUnused={} #misnomer. we don't use them for fitting
groupSumHistograms={}

skip=[]

channels=[channel for channel in dataChannelNamesSorted if not channel in skip]


print('putting together {} root files for: {}'.format(len(inFiles),dateString))

for root in inFiles:

    #skip if this root file is too small <10M 
    if os.stat(directory+root).st_size<10000000:
        continue

    allChannelsOK=True
    groupSumHistogramsToAdd={}
    dateTimeBatch=re.search(r'(\d{6})T\d{4}_\d{1,}',root).group(0)
    print('                                      \r',dateTimeBatch,end='\r')

    #open file and load events
    try:
        #sometimes this step fails with weird error
        rootFileOpen=uproot.open(directory+root)['daq']
        eventsByChannel=rootFileOpen.arrays(filter_name=channels,library='np')
        alphaEvents=rootFileOpen.arrays(filter_name='adc_b4_ch12',library='np')['adc_b4_ch12']
    except Exception as e:
        print(' '+dateTimeBatch,' no good: ',e)
        continue
    nChannels=len(channels)

    #get mask corresponding to alpha lightbulb
    alphaEventMaxima=np.empty([0])
    alphaEventMaximumTimes=np.empty([0])
    for event in alphaEvents:
        normPosEvent=np.median(event)-event
        alphaEventMaxima=np.append(alphaEventMaxima,np.max(normPosEvent)*voltageFactor)
        alphaEventMaximumTimes=np.append(alphaEventMaximumTimes,np.argmax(normPosEvent)*2)
    alphaMask=alphaEventMaxima>16 #16 mV alpha peak cut



    #loop and process each channel
    for channel in channels:
        print('                                      \r',dateTimeBatch,channel,end='\n' if channel==channels[-1] else '\r')
        events=eventsByChannel[channel]

        dataFraction=1 #can use a fraction of events for large file sets, testing
        fracMask=[(not bool(event%math.floor(1/dataFraction))) for event in range(len(events))]

        preProcessingmask=np.logical_and(alphaMask,fracMask) #doesn't vary from channel to channel within root file
        events=events[preProcessingmask]

        numEvents=len(events)
        eventMaxima=np.empty([0])
        eventMaximumTimes=np.empty([0])
        try: #only add processed events to hist if all channels are OK
            for event in events:
                normPosEvent=np.median(event)-event
                eventMaxima=np.append(eventMaxima,np.max(normPosEvent)*voltageFactor)
                eventMaximumTimes=np.append(eventMaximumTimes,np.argmax(normPosEvent)*2)
            peakMask=eventMaxima>2 # 2 mV peak cut to remove grossness

            regionOfInterestMaxima=np.empty([0])
            regionOfInterestCharges=np.empty([0])
            regionOfInterestInterval=findRoi(eventMaximumTimes,peakMask=peakMask)
            for event in events:
                normPosEvent=np.median(event)-event
                regionOfInterest=normPosEvent[regionOfInterestInterval[0]//2:regionOfInterestInterval[1]//2]
                regionOfInterestMaxima=np.append(regionOfInterestMaxima,np.max(regionOfInterest)*voltageFactor)
                regionOfInterestCharges=np.append(regionOfInterestCharges,np.sum(regionOfInterest)*2*voltageFactor*(1/50))
            #fraction of events containing hits
            freq=np.sum(np.logical_and.reduce((regionOfInterestInterval[0]<=eventMaximumTimes,eventMaximumTimes<regionOfInterestInterval[1],2<eventMaxima)))/numEvents if numEvents else -1
        
        except Exception as e:
            print(' '+dateTimeBatch,' no good:',e)
            allChannelsOK=False
            break
        
        pedestalMask=[mV>5 for mV in regionOfInterestMaxima]

        postProcessingMask=np.logical_and.reduce((pedestalMask,)) #can vary from channel to channel

        #put data in histogram. after this point most of the information is lost
        histData=regionOfInterestCharges[postProcessingMask]
        h,edges=np.histogram(histData,bins=np.linspace(-0.25,6.5,201))

        #keep one hist with all (ie incl. pedestal) data
        unused,edges=np.histogram(regionOfInterestCharges,bins=np.linspace(-0.25,6.5,201))

        if channel in speHistograms:
            speHistograms[channel]+=h
        else:
            speHistograms[channel]=h

        if channel in speHistogramsUnused:
            speHistogramsUnused[channel]+=unused
        else:
            speHistogramsUnused[channel]=unused

        if channel in groupSumHistogramsToAdd:
            groupSumHistogramsToAdd[channel]=np.append(groupSumHistogramsToAdd[channel],regionOfInterestCharges())
        else:
            groupSumHistogramsToAdd[channel]=regionOfInterestCharges
    
    #only add summed data to group hists if all channels have been processed so no channel is overweighted
    if allChannelsOK:
        for channel in channels:
            if channel in groupSumHistograms:
                groupSumHistograms[channel]=np.append(groupSumHistograms[channel],groupSumHistogramsToAdd[channel])
            else:
                groupSumHistograms[channel]=groupSumHistogramsToAdd[channel]


#perform a fit on the SPE peak of each histogram. we'll end up with a bunch of plots that we can save for diagnostic purposes
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

plt.figure(figsize=[20,nChannels])

results={} #these are what we eventually export in the csv file

p0={channel:[1,0.4,1e5] for channel in channels}

for n,channel in enumerate(channels):
    ax=plt.subplot(math.ceil(nChannels/4),4,n+1)
    print('                      \r'+'fitting '+channel,end='\n' if channel==channels[-1] else '\r')

    h=(speHistograms[channel],np.linspace(-0.25,6.5,201))
    unused=(speHistogramsUnused[channel],np.linspace(-0.25,6.5,201))

    modeBin=np.argmax(h[0])#initially find mode to fit around
    modeCharge=h[1][modeBin]
    xdata = ((h[1][1:]+h[1][:-1])/2)
    xmask=[(modeCharge-0.5)<charge<(modeCharge+0.5) for charge in xdata] #domain we will be fitting in relative to mode
    ydata = h[0][xmask]
    xdata=xdata[xmask]

    #fitting is computationally cheap. do an initial fit around the mode to try and find a good region for the final fit. maybe it will help
    poptInit,pcovInit=curve_fit(gauss,xdata,ydata,p0=p0[channel])
    xdata = ((h[1][1:]+h[1][:-1])/2)
    xmask=[(poptInit[0]-0.5)<charge<(poptInit[0]+0.5) for charge in xdata]
    ydata = h[0][xmask]
    xdata=xdata[xmask]

    #for real fit

    popt,pcov=curve_fit(gauss,xdata,ydata,p0=p0[channel])
    meanErr=calc1SigmaGaussianMeanError(xdata,ydata,popt)
    widthErr=calc1SigmaGaussianWidthError(xdata,ydata,popt)

    #err = np.sqrt(np.diag(pcov))

    dof=len(xdata)-2

    #add all information we think we'll want to the dictionary entry for this channel
    results[channel]={ 'ch_id':int(channel[5:6]+('0' if len(channel[9:])==1 else '')+channel[9:]),
                       'ch_name':channel,
                       'pmt':channelPMTNames[channel],
                       'spe_mean': popt[0],
                       'spe_width': popt[1],
                       'chi2': calc_chi2(gauss,xdata,ydata,popt),
                       'dof': dof,
                       'spe_mean_err': meanErr,
                       'spe_width_err': widthErr,
                       'HV':channelHVValues[channel],
                       }
    
    #normalize the histogram each channel in the group sums so that it's in SPE instead of pC
    groupSumHistograms[channel]=groupSumHistograms[channel]/popt[0]

    #plot the fit
    plt.stairs(*h,fill=True,color='blue')
    plt.stairs(*unused,color='orange')
    a=np.linspace((poptInit[0]-0.5),(poptInit[0]+0.5),350)
    trend=plt.plot(a,gauss(a,*popt),color='red')
    plt.xlabel('SPE Area [pC]')
    plt.xlim(-0.5, 6.5)
    plt.vlines(popt[0], 0, 1e5, color='grey', linestyle='dashed', label='maximum = {}'.format(round(popt[0],3)))
    plt.legend(title=channel,title_fontproperties={'weight':'bold'})
    plt.yscale('log')
    
plt.tight_layout()
output_directory = '/home/darik/plots/'
os.makedirs(output_directory, exist_ok=True)
plt.savefig(output_directory + date+'diagnosticplot.png')

import pandas as pd

pd.DataFrame(results).transpose().to_csv('/media/disk_a/WbLS-DATA/csv/phase6/bnl1t_spe_fit_results_'+date+'.csv',index=False)

#file to output group histogram fit data

csvOutputFile='sumSPE_phase6.csv'
try:
    df=pd.read_csv(csvOutputFile,header=[0,1],index_col=0)
except FileNotFoundError:
    df=pd.DataFrame(columns=pd.MultiIndex.from_product([['12','34','567','bottom','all'],['mean','meanErr','max']]))

plt.figure(figsize=(6.4*3,4.8*2))

#fit average num of PE detected in each group of PMTs

for n,group in enumerate(['all','upper','lower','middle','bottom']):
    if group=='all':
        histRange=44 #top end of histogram. set higher when more PE are detected on average
        total=np.sum(np.array([groupSumHistograms[channel] for channel in channels]),axis=0)
    elif group=='bottom':
        histRange=20
        total=np.sum(np.array([groupSumHistograms[channel] for channel in bottomChannels if not channel in skip]),axis=0)
    elif group=='upper':
        histRange=10
        total=np.sum(np.array([groupSumHistograms[channel] for channel in upperChannels if not channel in skip]),axis=0)
    elif group=='lower':
        histRange=10
        total=np.sum(np.array([groupSumHistograms[channel] for channel in lowerChannels if not channel in skip]),axis=0)
    else:
        histRange=20
        total=np.sum(np.array([groupSumHistograms[channel] for channel in middleChannels if not channel in skip]),axis=0)
    
    numBins=(histRange+5)*4

    ax=plt.subplot(2,3,n+1)

    #fit gaussian around pedestal and then remove it from data so fit is easier
    hPedestal=np.histogram(total,bins=np.linspace(-5,1,25),density=False)
    
    xdataPedestal = ((hPedestal[1][1:]+hPedestal[1][:-1])/2)
    xmaskPedestal=[-2<charge<0 for charge in xdataPedestal]
    ydataPedestal = hPedestal[0][xmaskPedestal]
    xdataPedestal=xdataPedestal[xmaskPedestal]

    poptPedestal,pcovPedestal=curve_fit(lambda xdata,sigma,scale:gauss(xdata,0,sigma,scale),xdataPedestal,ydataPedestal)

    #histogram of all charges
    h=np.histogram(total,bins=np.linspace(-5,histRange,numBins+1),density=False)
    xdata=((h[1][1:]+h[1][:-1])/2)

    #correct y data by subtracting pedestal, note that values are now floats since we're subtracting floats from them
    ydata=h[0]-gauss(xdata,0,poptPedestal[0],poptPedestal[1])
    plt.hist(xdata,h[1][:-1],weights=ydata)
    plt.hist(total,bins=numBins,range=(-5,histRange),density=False,histtype='step',color='orange')

    mode=xdata[np.argmax(ydata)]
    xmask=[(mode-histRange/8)<charge<(mode+histRange/8) for charge in xdata]
    xdataInit=xdata[xmask]
    ydataInit=ydata[xmask]

    #fitting is fast, do an initial fit to find center to fit around
    poptInit,pcovInit=curve_fit(gauss,xdataInit,ydataInit,p0=[mode,2,1e4])
    xmask=[(poptInit[0]-histRange/8)<charge<(poptInit[0]+histRange/8) for charge in xdata]
    xdata=xdata[xmask]
    ydata=ydata[xmask]
    popt,pcov=curve_fit(gauss,xdata,ydata,p0=[poptInit[0],poptInit[1],poptInit[2]])
    meanErr=np.sqrt(pcov[0][0])

    #widthErrs=calc1SigmaGaussianWidthError(xdata,ydata,popt)

    #using 99.9 pctile data value as max, just to remove possible outliers
    hist999=np.sort(total)[math.floor(0.999*len(total))]

    #hist995=np.sort(total)[math.floor(0.995*len(total))]
    #hist990=np.sort(total)[math.floor(0.99*len(total))]
    df.loc[date,(group,'mean')]=popt[0]
    df.loc[date,(group,'max')]=hist999
    df.loc[date,(group,'meanErr')]=meanErr

    #plot fitted data
    a=np.linspace(poptInit[0]-(histRange/8),poptInit[0]+(histRange/8),350)
    plt.plot(a, gauss(a,popt[0],popt[1],popt[2]), color='red',label='Gaussian Fit')
    plt.vlines(popt[0],0,1.1*np.max(ydata),color='black',linestyle='dashed')
    plt.xlabel('Photoelectrons per event')

df.to_csv(csvOutputFile)
plt.tight_layout()
plt.savefig(output_directory+date+'LYplot.png',format='png')
print('done with {}'.format(dateString))
exit(1)

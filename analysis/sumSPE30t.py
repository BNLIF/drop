#get a list of the files we're going to use


import sys
from datetime import datetime
import os

directory='/media/disk_f/30t-DATA/raw_root/phase0/'
date=sys.argv[1]
dateString=datetime.strptime(date,'%y%m%d').strftime('%d %b %Y')
allRootFiles=os.listdir(directory)
inFiles=list(filter(lambda file: date in file,allRootFiles))

if not inFiles:
    directory='/media/disk_c/WbLS-DATA/raw_root/phase3/muon/'
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
from scipy.optimize import curve_fit
def expDecay(f,f0,d,offset):
        return offset+f0*np.exp(-d*f)

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

skip=['adc_b3_ch0','adc_b3_ch1','adc_b3_ch2','adc_b3_ch3']

channels=[channel for channel in dataChannelNamesSorted30t if not channel in skip]


print('putting together {} root files for: {}'.format(len(inFiles),dateString))
import matplotlib.pyplot as plt
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
        alphaEvents=rootFileOpen.arrays(filter_name='adc_b3_ch13',library='np')['adc_b3_ch13']
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
    alphaMask=alphaEventMaxima>50 #1500 mV alpha peak cut. should be NIM signal usually



    #loop and process each channel
    for channel in channels:
        print('                                      \r',dateTimeBatch,channel,end='\n' if channel==channels[-1] else '\r')
        events=eventsByChannel[channel]
        events=(np.median(events)-events)*voltageFactor #now zeroed, positive-going, and in millivolts
        dataFraction=1 #can use a fraction of events for large file sets, testing
        fracMask=[(not bool(event%math.floor(1/dataFraction))) for event in range(len(events))]

        preProcessingMask=np.logical_and.reduce((alphaMask,fracMask,)) #the same for each batch of events in a root file
        events=events[preProcessingMask]

        numEvents=len(events)
        eventMaxima=np.empty([0])
        eventMaximumTimes=np.empty([0])
        
        averageSignalAmplitude=np.zeros(int(len(events[0])/2))
        addedSignalEvents=0
        averageNoiseAmplitude=np.zeros(int(len(events[0])/2))
        addedNoiseEvents=0
        
        try: #only add processed events to hist if all channels are OK
            
            for event in events:
                if (np.min(event)<-2) and (np.max(event)<5): #very pure noise
                    addedNoiseEvents+=1
                    fourierTransformAmplitude=np.abs((np.fft.fft(event)))
                    positiveAmplitude=fourierTransformAmplitude[0:int(len(fourierTransformAmplitude)/2)]
                    averageNoiseAmplitude+=positiveAmplitude
                if (np.min(event)>-5) and (np.max(event)>10): #very pure signal
                    addedSignalEvents+=1
                    fourierTransformAmplitude=np.abs((np.fft.fft(event)))
                    positiveAmplitude=fourierTransformAmplitude[0:int(len(fourierTransformAmplitude)/2)]
                    averageSignalAmplitude+=positiveAmplitude
                    
            noiseBad=addedNoiseEvents>0.01*len(events)
            if noiseBad:
                averageNoiseAmplitude/=addedNoiseEvents
                averageSignalAmplitude/=addedSignalEvents
                fourierTransormFrequency=np.fft.fftfreq(len(events[0]),d=2e-9)
                positiveFrequencies=fourierTransormFrequency[0:int(len(fourierTransormFrequency)/2)]
                popt,pcov=curve_fit(expDecay,positiveFrequencies[:int(len(positiveFrequencies)/2)],averageSignalAmplitude[:int(len(positiveFrequencies)/2)],p0=[200,4e-8,10])
                bigPhi=np.power(expDecay(positiveFrequencies,*popt),2)/(np.power(expDecay(positiveFrequencies,*popt),2)+np.power(averageNoiseAmplitude,2))
                bigPhiMask=np.concat([bigPhi[::-1],bigPhi])
                
                for n,event in enumerate(events):
                    fourierTransform=np.fft.fftshift(np.fft.fft(event)) #applying fourier transform mask
                    fourierTransform*=bigPhiMask
                    fourierTransform=np.fft.ifftshift(fourierTransform)
                    event=np.abs(np.fft.ifft(fourierTransform)) #should have a lot less high frequency noise
                    events[n]=event-np.median(event) #fourier filter tends to shift baseline
                    
                    eventMaxima=np.append(eventMaxima,np.max(event)) #get maximum times and voltages
                    eventMaximumTimes=np.append(eventMaximumTimes,np.argmax(event)*2)
            
            else:
                for n,event in enumerate(events):
                    eventMaxima=np.append(eventMaxima,np.max(event)) #get maximum times and voltages
                    eventMaximumTimes=np.append(eventMaximumTimes,np.argmax(event)*2)
                
            peakMask=eventMaxima>2 # 2 mV peak cut to remove grossness

            regionOfInterestMaxima=np.empty([0])
            regionOfInterestMinima=np.empty([0])
            regionOfInterestCharges=np.empty([0])
            regionOfInterestInterval=findRoi(eventMaximumTimes,peakMask=peakMask)
            
            for event in events:
                
                regionOfInterest=event[regionOfInterestInterval[0]//2:regionOfInterestInterval[1]//2]
                regionOfInterestMaxima=np.append(regionOfInterestMaxima,np.max(regionOfInterest))
                regionOfInterestMinima=np.append(regionOfInterestMinima,np.min(regionOfInterest))
                regionOfInterestCharges=np.append(regionOfInterestCharges,np.sum(regionOfInterest)*2*(1/50))
                
            #fraction of events containing hits
            freq=np.sum(np.logical_and.reduce((regionOfInterestInterval[0]<=eventMaximumTimes,eventMaximumTimes<regionOfInterestInterval[1],2<eventMaxima)))/numEvents if numEvents else -1
        
        except Exception as e:
            print(' '+dateTimeBatch,' no good:',e)
            allChannelsOK=False
            break
        
        pedestalMask=[mV>2.5 for mV in regionOfInterestMaxima]
        eventMinMask=[mV>-5 for mV in regionOfInterestMinima] #exclude signals that have noise in ROI
        postProcessingMask=np.logical_and.reduce((pedestalMask,eventMinMask,)) #can vary by channel

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



plt.figure(figsize=[20,nChannels])

results={} #these are what we eventually export in the csv file

p0={channel:[1,0.4,1e5] for channel in channels}

for n,channel in enumerate(channels):
    ax=plt.subplot(math.ceil(nChannels/4),4,n+1)
    print('                      \r'+'fitting '+channel,end='\n' if channel==channels[-1] else '\r')

    h=(speHistograms[channel],np.linspace(-0.25,6.5,201))
    unused=(speHistogramsUnused[channel],np.linspace(-0.25,6.5,201))
    
    plt.legend(title=channel,title_fontproperties={'weight':'bold'})
    plt.yscale('log')
    plt.stairs(*h,fill=True,color='blue')
    plt.stairs(*unused,color='orange')
    plt.xlabel('SPE Area [pC]')
    plt.xlim(-0.5, 6.5)
    try:
        modeBin=np.argmax(h[0])#initially find mode to fit around
        modeCharge=h[1][modeBin]
        xdata = ((h[1][1:]+h[1][:-1])/2)
        xmask=[(modeCharge-0.5)<charge<(modeCharge+0.5) for charge in xdata] #domain we will be fitting in relative to mode
        ydata = h[0][xmask]
        xdata=xdata[xmask]

        #fitting is computationally cheap. do an initial fit around the mode to try and find a good region for the final fit. maybe it will help
        poptInit,pcovInit=curve_fit(gauss,xdata,ydata,p0=p0[channel])
        xdata = ((h[1][1:]+h[1][:-1])/2)
        xmask=[(poptInit[0]-0.5)<charge<(poptInit[0]+0.3) for charge in xdata]
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
        
        a=np.linspace((poptInit[0]-0.5),(poptInit[0]+0.3),350)
        trend=plt.plot(a,gauss(a,*popt),color='red')
        plt.vlines(popt[0], 0, 1e5, color='grey', linestyle='dashed', label='maximum = {}'.format(round(popt[0],3)))
    except:
        print('fit didn\'t work for this day! adjust parameters maybe?')
        exit(0)
    
    
plt.tight_layout()
plt.savefig('diagnostics/30t/'+date+'diagnosticplot.png')

import pandas as pd

pd.DataFrame(results).transpose().to_csv('/media/disk_e/30t-DATA/csv/bnl30t_spe_fit_results_'+date+'.csv',index=False)


print('done with {}'.format(dateString))
exit(1)
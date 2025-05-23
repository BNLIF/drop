#%% setup
import sys
from wbls_functions import *
import numpy as np 
import pandas as pd
import uproot
from collections import defaultdict
from wbls_vars import *
from math import floor

voltageFactor=2000/(pow(2,14)-1)


directory='/media/disk_k/WbLS-DATA' #directory containing root files
root=directory+'/raw_root/phase8/muon/'+sys.argv[1]

import re
dateString=(re.search(r'(\d{6})T\d{4}',root).group(0) if re.search(r'(\d{6})T\d{4}',root) else '')

df=pd.read_csv(directory+'/csv/phase8/'+sys.argv[2],index_col='ch_name') # the calibration file. you'll have to put this in manually. a nice step to take would be trying to find the right calibration file automatically

skip=[]

channels=[channel for channel in dataChannelNamesSorted if not channel in skip]

#get events corresponding to top paddles triggering. haven't implemented hodoscope yet
with uproot.open(root)['daq'] as rootFileOpen:
    eventsByChannel=rootFileOpen.arrays(filter_name=channels,library='np')
    tp1Events=rootFileOpen.arrays(filter_name='adc_b4_ch13',library='np')['adc_b4_ch13']
    tp2Events=rootFileOpen.arrays(filter_name='adc_b4_ch14',library='np')['adc_b4_ch14']

    tp1EventMaxima=np.empty([0])
    tp1EventMaximumTimes=np.empty([0])
    tp2EventMaxima=np.empty([0])
    tp2EventMaximumTimes=np.empty([0])
    for event in tp1Events:
        normPosEvent=np.median(event)-event
        tp1EventMaxima=np.append(tp1EventMaxima,np.max(normPosEvent)*voltageFactor)
        tp1EventMaximumTimes=np.append(tp1EventMaximumTimes,np.argmax(normPosEvent)*2)
    for event in tp2Events:
        normPosEvent=np.median(event)-event
        tp2EventMaxima=np.append(tp2EventMaxima,np.max(normPosEvent)*voltageFactor)
        tp2EventMaximumTimes=np.append(tp2EventMaximumTimes,np.argmax(normPosEvent)*2)
    tpMask=np.logical_and(tp1EventMaxima>2,tp2EventMaxima>2) 


#correct daisy-chain delay so events are sync'd across boards
        
correctedLength=1800
numEvents=len(eventsByChannel['adc_b1_ch1'])

import json
with open('alpha_time_correction.json', 'r') as myfile:
    data=myfile.read()
obj = json.loads(data)
timeCorrections={}
for ch in dataChannelNamesSorted:
    if ch not in nonSignalChannels:
        pmt=channelPMTNames[ch]
        if pmt[:2] in ['bt','b1','b2','b3','b4']:
            timeCorrections[ch]=obj[pmt]
        else:
            timeCorrections[ch]=5
        if 'b1' in ch:
            timeCorrections[ch]+=144
        if 'b2' in ch:
            timeCorrections[ch]+=96
        if 'b3' in ch:
            timeCorrections[ch]+=48


tubesCorrected=defaultdict(list)
for tube in eventsByChannel:
        corr=int(timeCorrections[tube]/2)
        for n,event in enumerate(eventsByChannel[tube]):
            event=event[corr:(correctedLength+corr)]
            tubesCorrected[tube].append(event)
                

#%% main loop

def charge(event,start,stop):
    event=event[start:stop]
    area=np.trapezoid(event)
    return area*(2)/50

def findPEPeaks(event,threshold,integrationWidth):
    eventByCharge=np.array([charge(event,point-floor(integrationWidth/2),point+floor(integrationWidth/2)) for point in range(floor(integrationWidth/2),len(event)-floor(integrationWidth/2))])
    risingEdges=[]
    fallingEdges=[]
    for n in range(len(eventByCharge)-1):
        if eventByCharge[n]<threshold and threshold<eventByCharge[n+1]:
            risingEdges.append(n)
        if threshold<eventByCharge[n] and eventByCharge[n+1]<threshold:
            fallingEdges.append(n+1)
    if len(fallingEdges)>len(risingEdges):
        fallingEdges=fallingEdges[1:]
    if len(fallingEdges)<len(risingEdges):
        fallingEdges.append(len(event))
    peakTimes=[]
    peaks=[]
    for n,risingEdge in enumerate(risingEdges):
        fallingEdge=fallingEdges[n]
        if fallingEdge<risingEdge:
            return np.array([]),np.array([]),eventByCharge
        maxChargeTime,maxCharge=np.argmax(eventByCharge[risingEdge:fallingEdge]),np.max(eventByCharge[risingEdge:fallingEdge])
        peakTimes.append(maxChargeTime+risingEdge+floor(integrationWidth/2))
        peaks.append(maxCharge)
    return np.array(peakTimes),np.array(peaks),eventByCharge


tubesCorrectedSum=np.zeros((numEvents,correctedLength))
for n in range(len(tubesCorrectedSum)):
    for tube in tubesCorrected:
        toAdd=(np.median(tubesCorrected[tube][n])-tubesCorrected[tube][n])*voltageFactor
        tubesCorrectedSum[n]+=toAdd/df.loc[tube,'spe_mean']

toWrite=pd.DataFrame(columns=['peakTime','peakTotal']+list(tubesCorrected.keys()))
i=0
r=0
integrationWidth=30


for i,event in enumerate(tubesCorrectedSum):
    if tpMask[i]:
        peakTimes,peaks,eventByCharge=findPEPeaks(event,10,integrationWidth)
        goodEvent=False
    
        #actual cuts on events
        if len(peakTimes)==2:
            if 250<(peakTimes[-1]-peakTimes[0])<1500:
                if peaks[0]<=100:
                    peakTimes1,peakTimes2=peakTimes[0],peakTimes[-1]
                    goodEvent=True
        
        if goodEvent:
            toAddDict={}
            toAddDict['peakTime']=[(peakTimes2-peakTimes1)*2]
            toAddDict['peakTotal']=[0]
            for tube in tubesCorrected:
                
                c=charge((np.median(tubesCorrected[tube][i])-tubesCorrected[tube][i])*voltageFactor,peakTimes2-floor(integrationWidth/2),peakTimes2+floor(integrationWidth/2))/df.loc[tube,'spe_mean']
                toAddDict[tube]=[c]
                toAddDict['peakTotal'][0]+=c
            
            #print(charge(event,peakTimes2-floor(integrationWidth/2),peakTimes2+floor(integrationWidth/2)))
            toWrite=pd.concat((toWrite,pd.DataFrame(toAddDict)),ignore_index=True)
            r+=1

print('{}:{} decays ({} of total)'.format(dateString,r,(r/i if i!=0 else 0)))


#%% write output
if r/i<0.06:
    outputFile=dateString+'_muon.csv'
    toWrite.to_csv(outputFile)



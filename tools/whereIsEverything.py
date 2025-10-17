import sys
import os
import pandas as pd


startDate=pd.Timestamp(2024,6,1) #turned on the 30 ton in june 2024
endDate=pd.Timestamp.today() #might as well just step through everything up until today
outputFile="whereIsEverything.csv"

outputDF=pd.DataFrame(index=pd.date_range(startDate,endDate),
                      columns=pd.MultiIndex.from_product([['hasData','dataLocation','phase','numFiles','hasCSV','CSVLocation','CSVValidated'],["1t","30t"]]))

for date in outputDF.index:
    outputDF.loc[date,("hasData","1t")]=False
    outputDF.loc[date,("hasData","30t")]=False

    outputDF.loc[date,("dataLocation","1t")]=[]
    outputDF.loc[date,("dataLocation","30t")]=[]
    
    outputDF.loc[date,("phase","1t")]=0
    outputDF.loc[date,("phase","30t")]=0

    outputDF.loc[date,("numFiles","1t")]=[]
    outputDF.loc[date,("numFiles","30t")]=[]

    outputDF.loc[date,("hasCSV","1t")]=False
    outputDF.loc[date,("hasCSV","30t")]=False

    outputDF.loc[date,("CSVLocation","1t")]=[]
    outputDF.loc[date,("CSVLocation","30t")]=[]    
    
    
    outputDF.loc[date,("CSVValidated","1t")]=[]
    outputDF.loc[date,("CSVValidated","30t")]=[]
    
dataDirs=[os.path.join("/media",disk) for disk in os.listdir(r"/media") if "disk_" in disk]

import re
for dataDir in dataDirs:
    print(dataDir)
    for directory in os.walk(os.path.join(dataDir,"30t-DATA")):
        for currentDate in outputDF.index:
            
            dateString=currentDate.strftime("%y%m%d")
            rootWithThisDate=[file for file in directory[2] if (dateString in file and ".root" in file)]
            CSVWithThisDate=[file for file in directory[2] if (dateString in file and ".csv" in file)]

            if rootWithThisDate:
                
                outputDF.loc[currentDate,("hasData","30t")]=True
                outputDF.loc[currentDate,("dataLocation","30t")].append(directory[0])
                outputDF.loc[currentDate,("numFiles","30t")].append(len(rootWithThisDate))
                phase=re.search(r"phase(\d)",directory[0])
                if phase:
                    outputDF.loc[currentDate,("phase","30t")]=phase.group(1)          
                
            if CSVWithThisDate:
                outputDF.loc[currentDate,("hasCSV","30t")]=True
                outputDF.loc[currentDate,("CSVLocation","30t")].append(directory[0])
                outputDF.loc[currentDate,("CSVValidated","30t")].append("validated" in directory[0])
                    

    for directory in os.walk(os.path.join(dataDir,"WbLS-DATA")):
        for currentDate in outputDF.index:
            
            dateString=currentDate.strftime("%y%m%d")
            rootWithThisDate=[file for file in directory[2] if (dateString in file and ".root" in file)]
            CSVWithThisDate=[file for file in directory[2] if (dateString in file and ".csv" in file)]

            if rootWithThisDate:
                
                outputDF.loc[currentDate,("hasData","1t")]=True
                outputDF.loc[currentDate,("dataLocation","1t")].append(directory[0])
                outputDF.loc[currentDate,("numFiles","1t")].append(len(rootWithThisDate))
                phase=re.search(r"phase(\d)",directory[0])
                if phase:
                    outputDF.loc[currentDate,("phase","1t")]=phase.group(1)          
                
            if CSVWithThisDate:
                outputDF.loc[currentDate,("hasCSV","1t")]=True
                outputDF.loc[currentDate,("CSVLocation","1t")].append(directory[0])
                outputDF.loc[currentDate,("CSVValidated","1t")].append("validated" in directory[0])


outputDF.to_csv(outputFile)

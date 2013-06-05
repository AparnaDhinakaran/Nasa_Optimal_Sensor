#1st derivative, second derivative, moving mean, moving standard deviation, exponential smoothing

#import modules
import numpy as np
import scipy as sp
from scipy import stats
from numpy import vstack
import scikits.statsmodels.api as sm
import time
import datetime
from datetime import date
import matplotlib as mpl
from matplotlib import pyplot as plt
from time import mktime, localtime, gmtime, strftime
import math
import pdb
import DatabaseLight
import sqlite3
import facadeorientation

def smoothing(moteNum, nasa, smoothtype, movingStatsWindow=8, expWindow=12, Alpha=0.7):
    #define arrays
    data1=[]
    time1=[]
    hour1=[]
    ROC1=[]
    RROC1=[]
    mean1=[]
    stdev1=[]
    esmooth1=[]
    output=[]

    #get data
    #sensornumber=raw_input("Enter the sensor you are interested in:  ")
    sensornumber=moteNum
    if nasa:
        sensor='nasalight'+str(sensornumber)
    else:
        sensor='light'+str(sensornumber)
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        return 'bleh not ready yet'
    else:
        cursor.execute('SELECT light, unixtime, hour from %s WHERE unixtime>=1362175776000 AND unixtime<=1362729428000' %(sensor))
    x=0
    z1=cursor.fetchall()
    ##print len(z)
    for count in z1:
        if float(count[0])==1:
            x+=1
        if int(count[2])>=5 and int(count[2])<=20:
            if float(count[0])<=1:
                data1.append('nan')
            else:
                data1.append(float(count[0]))
        elif int(count[2])<5 or int(count[2])>20:
            data1.append(float(count[0]))
        time1.append(float(count[1]))
        hour1.append(float(count[2]))
        
    #print len(data)
    for count in range(len(data1)-1):
        if time1[count+1]-time1[count]<=6*300000 and data1[count]=='nan':
            data1[count]=np.mean(data1[count-8:count-1])
        elif time1[count+1]-time1[count]>6*300000 and data1[count]=='nan':
            data1[count]==1
            
    #rate of change
    for t in range(len(data1)-1):
        rate=data1[t+1]-data1[t]
        ROC1.append(rate)
        
    #rate of rate of change
    for n in range(len(ROC1)-1):
        changeofrate=ROC1[n+1]-ROC1[n]
        RROC1.append(changeofrate)
        
    #moving mean and standard deviation
    count=2
    w=int(movingStatsWindow)
    while count<=(len(data1)-w):
        average=np.mean(data1[count-w:count+w])
        std=np.std(data1[count-w:count+w])
        count+=1
        mean1.append((average,time1[count]))
        stdev1.append(std)

    #print "The lengths of mean, stdev, data, roc and rroc are", len(mean1),len(stdev1),len(data1),len(ROC1),len(RROC1)

    #exponential smoothing
    #introduce smoothing parameter

    p=expWindow
    alpha=Alpha
    for count in range(len(data1)):
        addsum1=0
        for add in range(int(p)-1):
            term=float(alpha)*math.pow((1-float(alpha)),add)*data1[count-add]
            addsum1+=term
        smoothed=addsum1+math.pow((1-float(alpha)),int(p))*data1[count-int(p)]
        esmooth1.append((smoothed, time1[count]))



    final=[time1,data1,mean1,esmooth1,ROC1,stdev1]
    if smoothtype=='exponential':
        output=final[3]
    elif smoothtype=='average':
        output=final[2]

    return output


    
        
    

    

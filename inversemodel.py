#THIS PROGRAM COMPUTES THE CORRELATION BETWEEN LIGHT LEVEL AND SUN ANGLE FOR 8 LEVELS OF CLOUDINESS AND TIME OF DAY (MORNING AND AFTERNOON)
#STEP#1:CLASSIFY DATA (BOTH SUN ANGLE AND LIGHT LEVEL) BY TIME OF DAY AND 8 CLOUDINESS LEVELS IN SEPARATE BINS
#STEP#2:PERFORM REGRESSION FOR EACH OF THE SIXTEEN BINS THUS CREATED


#print "This program computes correlation between sun position and received light from a dataset labelled by cloudiness and time of day, it does not scale for multiple windows"
#print "It first checks the number of one degree sun angle interval in database for a given cloudiness level and calls light levels for each degree angle"
#print "It then computes the correlation between daylight and indoor light for each cloudiness level and sun angle"

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
#Find the point biggest step change in daylight which will give the facade orientation for a given day from sun azimuth
#From the facade orientation it will be possible to find out how long the sun will be in this direction
#We will 4 consecutive clear days and compute the rate of change of illuminance and pick the time corresponding to majority days
#We then record the azimuth for this hour and assume this is the facade orientation

#Get zone orientation and time for which the zone faces direct sun
directsun=facadeorientation.orientation()
zone_orientation=directsun[1]
starttime=math.floor(float(directsun[2])+float(directsun[3])/60)
endtime=math.ceil(float(directsun[5])+float(directsun[6])/60)
#Get data from database
connection=sqlite3.connect('data.db')
cursor=connection.cursor()
#define dicts to save data
win_daylight=dict()
win_sunangle=dict()
win_hours=dict()
newwin_daylight=dict()
sensors=raw_input('Enter the number of sensors you want to draw the relationship for:  ')
cloudinessbins=raw_input('Enter the bin size for cloudiness (10 is maximum and 2 is minimum, 1,2,5,10 etc. enter even number): ')
bins=raw_input("Enter the bin size of sunangle in degrees:  ") #usually each sun angle bin is one degree, users can increase the bin size
cloudy=['Clear','Partly Cloudy','Scattered Clouds','Mostly Cloudy','Light Rain','Rain','Overcast','Heavy Rain','Fog','Haze'] #number of cloudiness could be user defined'''
n=0
getclouds=[]
while n+len(cloudy)/int(cloudinessbins)<=len(cloudy):
    cloudset=cloudy[n:n+len(cloudy)/int(cloudinessbins)]
    getclouds.append(cloudset)
    n=n+len(cloudy)/int(cloudinessbins)
for sensor in range(2,int(sensors)+2,1): #get values for each sensor in the room
    table='light'+str(sensor)
    daylight=dict()
    worklight=dict()
    sunangle=dict()
    hours=dict()
    newdaylight=dict()
    newsunangle=dict()
    coeffam=dict()
    constantam=dict()
    rvalueam=dict()
    sunangles=dict()
    sunanglerange=dict()
    for clouds in range(len(getclouds)): #for each level of cloudiness
        win_daylight[clouds]=[]
        win_sunangle[clouds]=[]
        win_hours[clouds]=[]
        hours[clouds]=[]
        newwin_daylight[clouds]=[]
        newdaylight[clouds]=[]
        newsunangle[clouds]=[]
        daylight[clouds]=[]
        sunangle[clouds]=[]
        sunanglerange[clouds]=[]
        sunangles[clouds]=[]
        getcloudiness=[]
        clouded=getclouds[clouds]
        getcloudiness.append(clouded)
        y1=[]
        y2=[]
        #print clouded
        for count in range(len(clouded)):
            cursor.execute('SELECT altitude, hour FROM light1 WHERE unixtime>=1.362175776e+12 AND unixtime<=1.362729428e+12 AND hour>=%s AND hour<=%s AND cloudiness="%s"' % (starttime,endtime,clouded[count]))
            y1.append(cursor.fetchall())
        n=0
        while n<=len(cloudy)/int(cloudinessbins)-1:
            for count in y1[n]:
                altitude=float(count[0])
                hour=int(count[1])
                if altitude>=0:
                    win_sunangle[clouds].append(altitude)
                    win_hours[clouds].append(hour)
            n+=1
        for count in range(len(clouded)):
            cursor.execute('SELECT altitude, hour FROM %s WHERE unixtime>=1.362175776e+12 AND unixtime<=1.362729428e+12 AND hour>=%s AND hour<=%s AND cloudiness="%s"' %(table,starttime,endtime,clouded[count]))
            y2.append(cursor.fetchall())
        n=0
        while n<=len(cloudy)/int(cloudinessbins)-1:
            for count in y2[n]:
                altitude=float(count[0])
                hour=int(count[1])
                if altitude>=0:
                    sunangle[clouds].append(altitude)
                    hours[clouds].append(hour)
            n+=1
        if len(sunangle[clouds])>len(win_sunangle[clouds]):
            datalength=len(win_sunangle[clouds])
        else:
            datalength=len(sunangle[clouds])
        win_daylight[clouds]=dict()
        daylight[clouds]=dict()
        coeffam[clouds]=dict()
        constantam[clouds]=dict()
        rvalueam[clouds]=dict()
        if len(sunangle[clouds])>1 and len(win_sunangle[clouds])>1:
            if max(sunangle[clouds])>=max(win_sunangle[clouds]):
                if min(sunangle[clouds])>=min(win_sunangle[clouds]):
                    sunanglerange[clouds]=np.arange(math.floor(min(sunangle[clouds])),math.ceil(max(win_sunangle[clouds])),int(bins))
                else:
                    sunanglerange[clouds]=np.arange(math.floor(min(win_sunangle[clouds])),math.ceil(max(win_sunangle[clouds])),int(bins))
            else:
                if min(sunangle[clouds])>=min(win_sunangle[clouds]):
                    sunanglerange[clouds]=np.arange(math.floor(min(sunangle[clouds])),math.ceil(max(sunangle[clouds])),int(bins))
                else:
                    sunanglerange[clouds]=np.arange(math.floor(min(win_sunangle[clouds])),math.ceil(max(sunangle[clouds])),int(bins))
        #print sunanglerange[clouds],clouded,clouds
        y3=dict()
        y4=dict()
        for angle in range(len(sunanglerange[clouds])-1):
            y3[angle]=[]
            for count in range(len(clouded)):
                cursor.execute('SELECT light FROM light1 WHERE unixtime>=1.362175776e+12 AND unixtime<=1.362729428e+12 AND hour>=%s AND hour<=%s AND cloudiness="%s" AND altitude>=%s AND altitude<=%s' % (starttime,endtime,clouded[count],sunanglerange[clouds][angle],sunanglerange[clouds][angle+1]))
                y3[angle].append(cursor.fetchall())
            #print sunanglerange[clouds][angle],y3[angle],clouded
            win_daylight[clouds][angle]=[]
            n=0
            while n<=len(cloudy)/int(cloudinessbins)-1:
                for count in y3[angle][n]:
                    if float(count[0])>1:
                        actualdaylight=round(float(count[0]),2)
                        win_daylight[clouds][angle].append(actualdaylight)
                n+=1
            #print len(win_daylight[clouds][angle]),' ',clouded,' ',sunanglerange[clouds][angle]
        for angle in range(len(sunanglerange[clouds])-1):
            y4[angle]=[]
            for count in range(len(clouded)):
                cursor.execute('SELECT light FROM %s WHERE unixtime>=1.362175776e+12 AND unixtime<=1.362729428e+12 AND hour>=%s AND hour<=%s AND cloudiness="%s" AND altitude>=%s AND altitude<=%s' % (table,starttime,endtime,clouded[count],sunanglerange[clouds][angle],sunanglerange[clouds][angle+1]))
                y4[angle].append(cursor.fetchall())
            daylight[clouds][angle]=[]
            coeffam[clouds][angle]=[]
            constantam[clouds][angle]=[]
            rvalueam[clouds][angle]=[]
            n=0
            while n<=len(cloudy)/int(cloudinessbins)-1:
                for count in y4[angle][n]:
                    if float(count[0])>1:
                        actualworklight=round(float(count[0]),2)
                        daylight[clouds][angle].append(actualworklight)
                n+=1
            #print len(daylight[clouds][angle]),' ',clouded,' ',sunanglerange[clouds][angle]
            if len(win_daylight[clouds][angle])>len(daylight[clouds][angle]):
                finaldatalength=len(daylight[clouds][angle])
            else:
                finaldatalength=len(win_daylight[clouds][angle])
            #filename="coefficients_"+str(sunanglerange[clouds][angle])+'_'+str(clouds)+".txt"
            filename="coefficients.txt"
            #savedata=open('C:\Users\chandrayee\Documents\GitHub\sensor-placement\\coefficients1_10_2sun\\'+filename,'a')
##PERFORM OLS
            if finaldatalength>2: 
                adata=vstack((win_daylight[clouds][angle][0:finaldatalength],daylight[clouds][angle][0:finaldatalength]))
                realadata=adata.transpose()
                x=realadata[:,0]
                y=realadata[:,1]
                X=sm.add_constant(x)
                model = sm.OLS(y, X).fit()
                if len(model.params)>1:
                    coeffam[clouds][angle]=round(model.params[0],3)
                    constantam[clouds][angle]=round(model.params[1],3)
                    rvalueam[clouds][angle]=round(model.rsquared,3)
            print "The coeff, constant and rvalue are", coeffam[clouds][angle], constantam[clouds][angle], rvalueam[clouds][angle], "for", clouded, "and angle", sunanglerange[clouds][angle]
            data=str(coeffam[clouds][angle])+'\t'+str(constantam[clouds][angle])+'\t'+str(rvalueam[clouds][angle])+'\t'+str(clouds)+'\t'+str(sunanglerange[clouds][angle])+'\n'      
            #savedata.write(data)
#savedata.close()      

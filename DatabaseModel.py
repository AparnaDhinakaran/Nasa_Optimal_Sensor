

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


def sunangle_range(sensor, num_sensors, inputcloudinessbins, num_bins):

#Get zone orientation and time for which the zone faces direct sun
    directsun = facadeorientation.orientation()
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
    sensors= num_sensors
    cloudinessbins= inputcloudinessbins
    bins=num_bins
    cloudy=['Clear','Partly Cloudy','Scattered Clouds','Mostly Cloudy','Light Rain','Rain','Overcast','Heavy Rain','Fog','Haze'] #number of cloudiness could be user defined'''
    n=0
    getcloudiness = []
    getclouds=[]
    while n+len(cloudy)/int(cloudinessbins)<=len(cloudy):
        cloudset=cloudy[n:n+len(cloudy)/int(cloudinessbins)]
        getclouds.append(cloudset)
        n=n+len(cloudy)/int(cloudinessbins)
    #for sensor in range(2,int(sensors)+2,1): #get values for each sensor in the room
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
        return sunanglerange[clouds]


def inverse_model(sensor, num_sensors, inputcloudinessbins, num_bins, angle):

#Get zone orientation and time for which the zone faces direct sun
    directsun = facadeorientation.orientation()
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
    sensors= num_sensors
    cloudinessbins= inputcloudinessbins
    bins=num_bins
    cloudy=['Clear','Partly Cloudy','Scattered Clouds','Mostly Cloudy','Light Rain','Rain','Overcast','Heavy Rain','Fog','Haze'] #number of cloudiness could be user defined'''
    n=0
    getcloudiness = []
    getclouds=[]
    while n+len(cloudy)/int(cloudinessbins)<=len(cloudy):
        cloudset=cloudy[n:n+len(cloudy)/int(cloudinessbins)]
        getclouds.append(cloudset)
        n=n+len(cloudy)/int(cloudinessbins)
    #for sensor in range(2,int(sensors)+2,1): #get values for each sensor in the room
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
        #return sunanglerange[clouds]
        y3=dict()
        y4=dict()
        #for angle in range(len(sunanglerange[clouds])-1):
        angle = angle_range
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
    #for angle in range(len(sunanglerange[clouds])-1):
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
        return [coeffam[clouds][angle], constantam[clouds][angle], rvalueam[clouds][angle], clouded, sunanglerange[clouds][angle]]










    


"""
    for angle in sunanglerange:
            to_db = ['direct', angle, float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN')]
            cursor.execute('INSERT INTO model' + sens_no + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_db)
            to_db = ['indirect', angle, float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN')]
            cursor.execute('INSERT INTO model' + sens_no + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_db)
                
    connection.commit()
            

def insertAllData():
    insert_modeldata(2,1,2,1)
    insert_model


def insert_modeldata(sens_no, num_sensors,angle):
    cloudbins = [2,5,10]
    deg_interval = [1,2]
    insert = []
    new_angle = angle
    for cloud in cloudbins:
        for deg in deg_interval:
            if (deg == 2):
                if (sunangle_range(sensor, num_sensors, inputcloudinessbins, num_bins)[0] % 2 == 0)
                    if ((angle % 2) != 0):
                        new_angle = angle - 1
                else:
                    if ((angle % 2) == 0):
                        new_angle = angle - 1;
            insertable = inverse_model(sens_no, num_sensors, cloud, deg,angle)
            insert.append(insertable)[0]
            insert.append(insertable)[1]
            insert.append(insertable)[2]
    to_db = ['direct', angle, insert[0], insert[1], insert[3], insert[4], insert[5], insert[6], insert[7], insert[8], insert[9], insert[10], insert[11], insert[12], insert[13], insert[14], insert[15], insert[16], insert[17], insert[18]) ]
    cursor.execute('INSERT INTO model' + sens_no + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_db)
            
    
"""

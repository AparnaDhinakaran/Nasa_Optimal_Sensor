
##### USER INFORMATION ##########
"""
This Python File will fill in the model tables that have the coefficients, constants, and R-values for the relationship between sunangles and cloudiness.
The corresponding tables are model1, model2, model3, nasamodel1, nasamodel2, nasamodel3, nasamodel4, nasamodel5, nasamodel6, nasamodel7, nasamodel8, and nasamodel9.
These tables were created when you ran the new create_tables.py
If you have not run the new create_tables.py then comment out the tables that you have already created, and run create_tables.py again.

The only function, on this file you will have to call is insertModelData().
It has no parameters and this function will create the model data for all the model tables.
"""

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



def utime():
    date=raw_input('Enter the date in day, month and year (as 25022013): ')
    data=[]
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    cursor.execute('SELECT unixtime FROM light1 WHERE day=? AND month=? AND year=?', (int(date[:2]),int(date[2:4]),int(date[4:])))
    for i in cursor.fetchall():
        data.append(float(i[0]))
    return data[0],data[-1]




def insertModelData():
    for sensor in range(2,5):
        create_skeleton_database(sensor, False)
        insert_model1(sensor, False)
        insert_model2(sensor, False)
        insert_model3(sensor, False)
        insert_model4(sensor,False)
        insert_model5(sensor, False)
        insert_model6(sensor, False)
        print "Inserted Model" + str(sensor)
    """for sensor in range(1,10):
        create_skeleton_database(sensor,True)
        insert_model1(sensor, True)
        insert_model2(sensor, True)
        insert_model3(sensor, True)
        insert_model4(sensor, True)
        insert_model5(sensor, True)
        insert_model6(sensor, True)"""

def inverse_model(sensor, num_sensors, num_cloud_bins, num_bins):
    returned = []
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
    sensors=num_sensors
    cloudinessbins=num_cloud_bins
    bins= num_bins
    cloudy=['Clear','Partly Cloudy','Scattered Clouds','Mostly Cloudy','Light Rain','Rain','Overcast','Heavy Rain','Fog','Haze'] #number of cloudiness could be user defined'''
    n=0
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
            #filename="coefficients.txt"
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
            #print "The coeff, constant and rvalue are", coeffam[clouds][angle], constantam[clouds][angle], rvalueam[clouds][angle], "for", clouded, "and angle", sunanglerange[clouds][angle]
            returned.append([sunanglerange[clouds][angle], clouded, coeffam[clouds][angle], constantam[clouds][angle], rvalueam[clouds][angle]])
    return returned
            #data=str(coeffam[clouds][angle])+'\t'+str(constantam[clouds][angle])+'\t'+str(rvalueam[clouds][angle])+'\t'+str(clouds)+'\t'+str(sunanglerange[clouds][angle])+'\n'      
            #savedata.write(data)
    #savedata.close()



def nasa_inverse_model(sensor, num_sensors, num_cloud_bins, num_bins):
    returned = []
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
    sensors=num_sensors
    cloudinessbins=num_cloud_bins
    bins= num_bins
    cloudy=['Clear','Partly Cloudy','Scattered Clouds','Mostly Cloudy','Light Rain','Rain','Overcast','Heavy Rain','Fog','Haze'] #number of cloudiness could be user defined'''
    n=0
    getclouds=[]
    while n+len(cloudy)/int(cloudinessbins)<=len(cloudy):
        cloudset=cloudy[n:n+len(cloudy)/int(cloudinessbins)]
        getclouds.append(cloudset)
        n=n+len(cloudy)/int(cloudinessbins)
    #for sensor in range(2,int(sensors)+2,1): #get values for each sensor in the room
    table='nasalight'+str(sensor)
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
            cursor.execute('SELECT altitude, hour FROM nasalight8 WHERE unixtime>=1337903413000.0 AND unixtime<=1338414791000.0 AND hour>=%s AND hour<=%s AND cloudiness="%s"' % (starttime,endtime,clouded[count]))
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
            cursor.execute('SELECT altitude, hour FROM %s WHERE unixtime>=1337903413000.0 AND unixtime<=1338414791000.0 AND hour>=%s AND hour<=%s AND cloudiness="%s"' %(table,starttime,endtime,clouded[count]))
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
                cursor.execute('SELECT light FROM nasalight8 WHERE unixtime>=1337903413000.0 AND unixtime<=1338414791000.0 AND hour>=%s AND hour<=%s AND cloudiness="%s" AND altitude>=%s AND altitude<=%s' % (starttime,endtime,clouded[count],sunanglerange[clouds][angle],sunanglerange[clouds][angle+1]))
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
                cursor.execute('SELECT light FROM %s WHERE unixtime>=1337903413000.0 AND unixtime<=1338414791000.0 AND hour>=%s AND hour<=%s AND cloudiness="%s" AND altitude>=%s AND altitude<=%s' % (table,starttime,endtime,clouded[count],sunanglerange[clouds][angle],sunanglerange[clouds][angle+1]))
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
            #filename="coefficients.txt"
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
            #print "The coeff, constant and rvalue are", coeffam[clouds][angle], constantam[clouds][angle], rvalueam[clouds][angle], "for", clouded, "and angle", sunanglerange[clouds][angle]
            returned.append([sunanglerange[clouds][angle], clouded, coeffam[clouds][angle], constantam[clouds][angle], rvalueam[clouds][angle]])
    return returned
            #data=str(coeffam[clouds][angle])+'\t'+str(constantam[clouds][angle])+'\t'+str(rvalueam[clouds][angle])+'\t'+str(clouds)+'\t'+str(sunanglerange[clouds][angle])+'\n'      
            #savedata.write(data)
    #savedata.close()


def insert_model1(sensor, nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        modeltable = "nasamodel" + str(sensor)
        insert = nasa_inverse_model(sensor,1,2,1)
    else:
        modeltable = "model" + str(sensor)
        insert = inverse_model(sensor, 1, 2, 1)
    for row in insert:
        angle = row[0]
        for cloud in row[1]:
            if row[2] == []:
                row[2]= float('NaN')
            if row[3] == []:
                row[3] = float('NaN')
            if row[4] == []:
                row[4]= float('NaN')
            cursor.execute('UPDATE ' + str(modeltable) + ' SET coefficient2_1 = ?, constant2_1 = ?, rsquared2_1 = ? WHERE sunangle = ? AND cloudiness = ? AND sunexposure = "direct"', (row[2], row[3], row[4], angle, cloud))
    connection.commit()

def insert_model2(sensor,nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        modeltable = "nasamodel" + str(sensor)
        insert = nasa_inverse_model(sensor,1,2,2)
    else:
        modeltable = "model" + str(sensor)
        insert = inverse_model(sensor, 1, 2, 2)
    for row in insert:
        angle = row[0]
        for cloud in row[1]:
            if row[2] == []:
                row[2]= float('NaN')
            if row[3] == []:
                row[3] = float('NaN')
            if row[4] == []:
                row[4]= float('NaN')
            cursor.execute('UPDATE ' + str(modeltable) + ' SET coefficient2_2 = ?, constant2_2 = ?, rsquared2_2 = ? WHERE sunangle = ? AND cloudiness = ? AND sunexposure = "direct"', (row[2], row[3], row[4], angle, cloud))
    connection.commit()


def insert_model3(sensor,nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        modeltable = "nasamodel" + str(sensor)
        insert= nasa_inverse_model(sensor,1,5,1)
    else:
        modeltable = "model" + str(sensor)
        insert = inverse_model(sensor, 1, 5, 1)
    for row in insert:
        angle = row[0]
        for cloud in row[1]:
            if row[2] == []:
                row[2]= float('NaN')
            if row[3] == []:
                row[3] = float('NaN')
            if row[4] == []:
                row[4]= float('NaN')
            cursor.execute('UPDATE ' + str(modeltable) + ' SET coefficient5_1 = ?, constant5_1 = ?, rsquared5_1 = ? WHERE sunangle = ? AND cloudiness = ? AND sunexposure = "direct"', (row[2], row[3], row[4], angle, cloud))
    connection.commit()

def insert_model4(sensor,nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        modeltable = "nasamodel" + str(sensor)
        insert = nasa_inverse_model(sensor,1,5,2)
    else:
        modeltable = "model" + str(sensor)
        insert = inverse_model(sensor, 1, 5, 2)
    for row in insert:
        angle = row[0]
        for cloud in row[1]:
            if row[2] == []:
                row[2]= float('NaN')
            if row[3] == []:
                row[3] = float('NaN')
            if row[4] == []:
                row[4]= float('NaN')
            cursor.execute('UPDATE ' + str(modeltable) + ' SET coefficient5_2 = ?, constant5_2 = ?, rsquared5_2 = ? WHERE sunangle = ? AND cloudiness = ? AND sunexposure = "direct"', (row[2], row[3], row[4], angle, cloud))
    connection.commit()


def insert_model5(sensor,nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        modeltable = "nasamodel" + str(sensor)
        insert = nasa_inverse_model(sensor,1,10,1)
    else:
        modeltable = "model" + str(sensor)
        insert = inverse_model(sensor, 1, 10, 1)
    for row in insert:
        angle = row[0]
        for cloud in row[1]:
            if row[2] == []:
                row[2]= float('NaN')
            if row[3] == []:
                row[3] = float('NaN')
            if row[4] == []:
                row[4]= float('NaN')
            cursor.execute('UPDATE ' + str(modeltable) + ' SET coefficient10_1 = ?, constant10_1 = ?, rsquared10_1 = ? WHERE sunangle = ? AND cloudiness = ? AND sunexposure = "direct"', (row[2], row[3], row[4], angle, cloud))
    connection.commit()

def insert_model6(sensor,nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    if nasa:
        modeltable = "nasamodel" + str(sensor)
        insert = nasa_inverse_model(sensor,1,10,2)
    else:
        modeltable = "model" + str(sensor)
        insert = inverse_model(sensor, 1, 10, 2)
    for row in insert:
        angle = row[0]
        for cloud in row[1]:
            if row[2] == []:
                row[2]= float('NaN')
            if row[3] == []:
                row[3] = float('NaN')
            if row[4] == []:
                row[4]= float('NaN')
            cursor.execute('UPDATE ' + str(modeltable) + ' SET coefficient10_2 = ?, constant10_2 = ?, rsquared10_2 = ? WHERE sunangle = ? AND cloudiness = ? AND sunexposure = "direct"', (row[2], row[3], row[4], angle, cloud))
    connection.commit()



def create_skeleton_database(sensor,nasa):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    cloudy=['Clear','Partly Cloudy','Scattered Clouds','Mostly Cloudy','Light Rain','Rain','Overcast','Heavy Rain','Fog','Haze']
    if nasa:
        table = "nasalight" + str(sensor)
    else:
        table = "light" + str(sensor)
    max_altitude = round((cursor.execute('SELECT MAX(altitude) FROM ' + table).fetchone())[0])
    if nasa:
        modeltable = "nasamodel" + str(sensor)
    else:
        modeltable = "model" + str(sensor)
    for angle in range(0, int(max_altitude)):
        for cloud in cloudy:
            to_db = [angle, cloud, "direct", float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'),float('NaN')]
            cursor.execute('INSERT INTO ' + modeltable  + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_db)
            to_db = [angle, cloud,'indirect', float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'), float('NaN'),float('NaN')]
            cursor.execute('INSERT INTO ' + modeltable  + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_db)
    connection.commit()                

        

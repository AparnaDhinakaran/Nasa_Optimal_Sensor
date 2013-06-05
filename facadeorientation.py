#print "This program calculates the facade orientation from rate of change of light level and determines the approximate length of the time for which the facade sees direct sun"
#print "Function orientation returns facade orientation"
#print "Function direct_sun returns the start time and the end time of the direct sun on the facade"
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
import pdb
import DatabaseLight
import sqlite3
import collections
from collections import Counter

#set up connection with server
connection=sqlite3.connect('data.db')
cursor=connection.cursor()
days=np.arange(1,20,1)
totalsunnyhours=[]
lastdate=[]
#TO FIND OUT THE FACADE ORIENTATION
#pick 4 days with maximum number of clear hours in a month
#find the time corresponding to maximum rate of increase of light level with coincides with first appearance of direct sun at the window
#determine the azimuth corresponding to the time which gives approximate facade orientation
#the time corresponding to maximum rate of decrease in light level may coincide with disappearance of direct sun
def orientation():
    for eachday in days:
        save=[]
        savedate=[]
        cursor.execute('SELECT cloudiness, day, month FROM light1 WHERE month=4 AND day=%s'% (eachday))
        y1=cursor.fetchall()
        for x in y1:
            save.append(x[0])
            savedate.append(str(x[1]))
        sunny1=save.count("Clear")
        sunny2=save.count("Scattered Clouds")
        lastdate.append(int(savedate[0]))                
        totalsunnyhours.append(sunny1+sunny2)
    indexlist=[i[0] for i in sorted(enumerate(totalsunnyhours), key=lambda x:x[1])][-4:]
    getdate = [lastdate[i] for i in indexlist]
    getstarthour=[] 
    getstartminute=[]
    getstartseconds=[]
    getendhour=[] 
    getendminute=[]
    getendseconds=[]
    for finaldays in getdate:
        light=[]
        hour=[]
        minute=[]
        change=[]
        day=[]
        seconds=[]
        y3=[]
        cursor.execute('SELECT light, hour, minute, seconds, day FROM light1 WHERE month=4 AND day=%s'% (finaldays))
        y2=cursor.fetchall()
        for data in y2:
            light.append(data[0])
            hour.append(data[1])
            minute.append(data[2])
            seconds.append(data[3])
            day.append(data[4])
        for count in range(len(light)-1):
            rateofchange=light[count+1]-light[count]
            change.append(rateofchange)
        getmaxindex=change.index(max(change))
        getminindex=change.index(min(change))
        getstarthour.append(hour[getmaxindex]) 
        getstartminute.append(minute[getmaxindex])
        getstartseconds.append(seconds[getmaxindex])
        getendhour.append(hour[getminindex]) 
        getendminute.append(minute[getminindex])
        getendseconds.append(seconds[getminindex])
    for count in range(len(getdate)):
        cursor.execute('SELECT azimuth FROM light1 WHERE month=4 AND day=? AND hour=? AND minute=? AND seconds=?',(getdate[count],getstarthour[count],getstartminute[count],getstartseconds[count]))
        y3.append(cursor.fetchall()[0][0])
    endhour=max(getendhour)
    endminute=getendminute[getendhour.index(max(getendhour))]
    enddate=getdate[getendhour.index(max(getendhour))]
    endseconds=getendseconds[getendhour.index(max(getendhour))]
    starthour=getstarthour[y3.index(min(y3))]
    startminute=getstartminute[y3.index(min(y3))]
    startseconds=getstartseconds[y3.index(min(y3))]
    cursor.execute('SELECT azimuth FROM light1 WHERE month=4 AND day=? AND hour=? AND minute=? AND seconds=?',(enddate,endhour,endminute,endseconds))
    y4=cursor.fetchall()
    return "The facade orientation and start and the end of direct sun visibility are ", round(np.mean(y3),2),starthour,startminute,startseconds,endhour,endminute,endseconds


    
    

    
    


                            

    
        
            
    


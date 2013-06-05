"""Code for extracting data from wunderground API and adding the data to the
cloud table of data.db.

The cloud table has the following 9 attributes (column names and types):

timezone string, year int, month int, day int, time string, unixtime REAL, cloudiness string, cloudvalue REAL, daycloudvalue REAL
"""

import urllib2
import datetime
import numpy as np
import sqlite3
from numpy import vstack
import scipy as sp
from scipy import stats
from datetime import datetime,date
import time
from time import mktime, localtime, gmtime, strftime
import statsmodels as sm
import matplotlib as mpl
from matplotlib import pyplot as plt
import pytz
from pytz import timezone
import math
import pdb

import sqlite3
from sqlite3 import dbapi2 as sqlite3

cloudiness=['Clear','Partly','Scattered','Light','Mostly','Rain','Overcast','Heavy','Fog','Haze']
values=[0,2,4,4,7,7,8,8,4,4]
clouddict = {'Clear': 0, 'Partly Cloudy':2, 'Scattered Clouds':4, 'Light Rain':4, 'Mostly Cloudy':7, 'Rain':7, 'Overcast':8, 'Heavy Rain':8, 'Fog':4, 'Haze':4}


def make_unix_timestamp(date_string, time_string):
    format = '%Y %m %d %H %M %S'
    return time.mktime(time.strptime(date_string + " " + time_string, format))
                       
    
def isLeapYear( year):
      if (year % 400 == 0) :
          return True
      if (year % 100 == 0) :
          return False
      if (year % 4 == 0):
          return True
      else:
          return False              
  

def daysInMonth(month,year):
      if (month == 2):
          if (isLeapYear(year)):
              return 29;
          else:
              return 28
      elif (month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12):
          return 31
      else :
          return 30
 
def dayInYear(month, day, year):
    current = 1
    numberOfDays = day
    while (current < month):
        numberOfDays = numberOfDays + daysInMonth(current, year)
        current = current + 1
    return numberOfDays

def difference(month1, day1, year1, month2, day2, year2):
    daycounter = 0;  
    if (year1 == year2):
        return (dayInYear(month1, day1, year1) - dayInYear(month2, day2,year2))
    elif (isLeapYear(year2)):
        daycounter = daycounter + (366 - dayInYear(month2, day2, year2))
    else:
        daycounter = daycounter + (365 - dayInYear(month2, day2, year2))
    daycounter = daycounter + dayInYear(month1, day1, year1)
    current = year2 + 1
    while (current < year1):
        if (isLeapYear(current)):
            daycounter = daycounter + 366
            current = current + 1
        else:
            daycounter = daycounter + 365
            current = current + 1
    return daycounter


def arrayofdaysmonthsyears(month1,day1,year1,month2,day2,year2):
    daysleftinmonth2 = daysInMonth(month2, year2) - day2 + 1
    if year1 == year2:
            if month1 == month2:
                monthsinbetween = 0
            else:
              monthsinbetween= month1 - month2 - 1
    else:
        monthsleftinyear2 = 12 - month2 - 1
        monthsinbetween = monthsleftinyear2 + (12 *(year1 - (year2+1))) + month1
    dayarray = []
    montharray = []
    yeararray= []
    if year1 == year2:
        if month2 == month1:
          currentdays = day1 - day2 + 1
        else:
            currentdays = daysleftinmonth2
    else:
        currentdays = daysleftinmonth2        
    currentday = day2
    currentmonth = month2
    currentyear = year2
    while currentdays > 0:
        dayarray.append(currentday)
        montharray.append(currentmonth)
        yeararray.append(currentyear)
        currentdays = currentdays - 1
        currentday = currentday + 1
    fullmonths = monthsinbetween
    currentmonth = month2 + 1
    while fullmonths > 0:
        if currentmonth > 12:
              currentmonth = 1
              currentyear = currentyear + 1
        daystoadd = daysInMonth(currentmonth, currentyear)
        currentdaytoadd = 1
        while daystoadd > 0:
            dayarray.append(currentdaytoadd)
            montharray.append(currentmonth)
            yeararray.append(currentyear)
            currentdaytoadd = currentdaytoadd + 1
            daystoadd = daystoadd - 1
        currentmonth = currentmonth + 1
        fullmonths = fullmonths - 1
    daysinday1 = day1
    finaldaytoadd = 1
    if month2 != month1 or year1 != year2:
          while daysinday1 > 0:
              dayarray.append(finaldaytoadd)
              montharray.append(month1)
              yeararray.append(year1)
              finaldaytoadd = finaldaytoadd + 1
              daysinday1 = daysinday1 - 1
    return [dayarray, montharray, yeararray]

def arrayofdays(month1,day1,year1,month2,day2,year2):
      return (arrayofdaysmonthsyears(month1,day1,year1,month2,day2,year2))[0]

def arrayofmonths(month1,day1,year1,month2,day2,year2):
      return (arrayofdaysmonthsyears(month1,day1,year1,month2,day2,year2))[1]

def arrayofyears(month1,day1,year1,month2,day2,year2):
      return (arrayofdaysmonthsyears(month1,day1,year1,month2,day2,year2))[2]

def day_cloudiness():
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    x = cursor.execute('SELECT unixtime from cloud')
    cloudtimes = []
    for i in x.fetchall():
        cloudtimes.append(i[0])
    for elem in cloudtimes:
        #elem = cloudtimes[0]
        day = (cursor.execute('SELECT day FROM cloud WHERE unixtime = ' + str(elem))).fetchall()[0][0]
        month = (cursor.execute('SELECT month FROM cloud WHERE unixtime = ' + str(elem))).fetchall()[0][0]
        year = (cursor.execute('SELECT year FROM cloud WHERE unixtime = ' + str(elem))).fetchall()[0][0]
        values = (cursor.execute('SELECT cloudvalue FROM cloud WHERE day = ' + str(day) + ' AND month = ' + str(month) + ' AND year = ' + str(year))).fetchall()
        total = 0;
        checker = False
        i = 0
        while i < len(values):
            if values[i][0] != float('nan') and values[i][0] != None:
                checker = True
                total = total + values[i][0]
            i = i + 1
        if checker:
            average = total/len(values)
        else:
            average = 'nan'
        cursor.execute('UPDATE cloud SET daycloudvalue = ? WHERE unixtime = ? ', (average, elem))
    connection.commit()
    
       

def createCloudData(end, start = "2012 09 07", feature = "history", station = "KOAK"):
    """Adds all the wunderground data to the cloud data starting from start
    date START until end date END. You can specify the feature FEATURE to pull
    either historical data or hourly data. You also must specify the weather
    station STATION. Default values are above."""
    #Connect to the database data.db
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    start_split = start.split()
    end_split = end.split()
    startyear = int(start_split[0])
    endyear = int(end_split[0])
    startmonth = int(start_split[1])
    endmonth = int(end_split[1])
    startday = int(start_split[2])
    endday = int(end_split[2])

    DD = arrayofdays(endmonth,endday,endyear,startmonth,startday,startyear)
    MM = arrayofmonths(endmonth,endday,endyear,startmonth,startday,startyear)
    YYYY = arrayofyears(endmonth,endday,endyear,startmonth,startday,startyear)
    
    for i in range(len(DD)):
        month = str(MM[i])
        day = str(DD[i])
        if (DD[i] < 10):
            day = "0" + day
        if (MM[i] < 10):
              month = "0" + month
        YYYYMMDD=str(YYYY[i])+month+day
        features=feature+"_"+YYYYMMDD
        url="http://api.wunderground.com/api/44f02142905d4c0b/"+features+"/q/"+station+".json"
        print(url)
        data=urllib2.urlopen(url).read()
        getdata=data.split(",")
        for count in range(len(getdata)):
            if '"tzname":' in getdata[count]:
                if '"tzname": "UTC"' not in getdata[count]:
                    minute = getdata[count-1].split(":")
                    y2 = minute[1].strip().replace("\"","")
                    if (y2 == "53"):
                        timezone = getdata[count].split(":")
                        x = timezone[1].replace("\"","").replace("}","").strip()
                        hour = getdata[count-2].split(":")
                        y1 = hour[1].strip().replace("\"","")
                        clouds = getdata[count+30].split(":")
                        cloudiness = clouds[1].replace("\"","")
                        if cloudiness in clouddict.keys(): 
                            cloudvalue = clouddict[cloudiness]
                        else:
                            cloudvalue = float('nan')
                        unixtime = make_unix_timestamp(str(YYYY[i]) + " " + month + " " + day, y1 + " " + y2 + " " + "00")
                        to_db = [x, YYYY[i], MM[i], DD[i], int(y1), int(y2), 0, unixtime, cloudiness,cloudvalue, float('nan')]
                        cursor.execute('INSERT OR IGNORE INTO cloud VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                               to_db)
        
    #Save your changes
    day_cloudiness()
    connection.commit()

def updateCloudData():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT year, month, day, MAX(unixtime) FROM cloud')
    #cursor.execute('SELECT MAX(unixtime) FROM cloud')
    current = cursor.fetchall()[0]
    #for i in cursor.fetchmany(2):
     #   print i
    #print(current)
    year = str(current[0])
    month = str(current[1])
    day = str(current[2])
    if month < 10:
          month = "0" + month
    if day < 10:
          day = "0" + day
    start = year + " " + month + " " + day
    ttb = time.localtime()
    end = strftime("%Y %m %d", ttb)
    #print(start)
    #print(end)
    createCloudData(end, start)

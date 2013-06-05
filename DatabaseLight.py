"""Code for extracting data from smap url's and adding the data to the
light tables of data.db. In addition to adding the raw data from the smap
url's, we also create sunposition data (altitude and azimuth) and add the
values as the 10th and 11th attributes of a light table.

The light tables (light1, light2, light3, etc.) have the following
attributes (column names and types):

unixtime float, weekday string, day int, month int, year int, hour int,
    minute int, seconds int,light float, altitude float, azimuth float,
    cloudiness TEXT, x REAL, y REAL, error2_1 REAL, error2_2 REAL,
    error5_1 REAL, error5_2 REAL, error10_1 REAL, error10_2 REAL,
"""

import numpy as np
from numpy import vstack
import scipy as sp
from scipy import stats
import urllib2
import datetime
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

#lat and lon global variables of BEST lab
best_lat = "37 52 27.447"
best_lon = "122 15 33.3864 W"
best_timezone = "US/Pacific"

#lat and lon global variables for NASA
nasa_lat = "37 24 54.7194"
nasa_lon = "122 2 53.8794 W"
nasa_timezone = "US/Pacific"

def change_loc(sens_no, nasa, new):
    """Changes the value of SENS_NO in the sensors_loc dictionary to the
    tuple NEW."""
    if nasa:
        nasa_sensors_loc[sens_no] = new
    else:
        sensors_loc[sens_no] = new

#Dictionary that maps each BEST lab sensor number to its location (x, y)
sensors_loc = {1:(0,0), 2:(0,1), 3:(1,0), 4:(1,1)}

#Dictionary that maps each NASA lab sensor number to its location (x, y)
nasa_sensors_loc = {1:(0,0), 2:(0,1), 3:(1,0), 4:(1,1), 5:(1,2), 6:(2,1),
                    7:(3,3), 8:(4,3), 9:(5,5)}

#Dictionary that maps each BEST lab sensor number to its sensor ID.
sensors_dict = {1:"7140b2da-94cd-5bae-a1e8-cb85a6715bf5",
                2:"f862a13d-91ee-5696-b2b1-b97d81a47b5b",
                3:"b92ddaee-48de-5f37-82ed-fe1f0922b0e5",
                4:"8bb0b6a2-971f-54dc-9e19-14424b9a1764"}

#Dictionary that maps each NASA lab sensor number to its sensor ID.
nasa_sensors_dict = {1:"6325ce7e-5afe-5301-bf11-391f10703998",
                     2:"473da30c-691f-532b-813d-10db0f9adc34",
                     3:"e82ad906-4fbf-5747-beff-72d0c5efccba",
                     4:"7a66bf12-4265-5139-9251-f33d12b93298",
                     5:"7e69270c-305b-5f1c-9dc5-995d594f2a34",
                     6:"06d693f6-1f6e-5746-ba99-ac49383b0a21",
                     7:"2ae4fa93-0f64-52b8-bd64-49c6850ee474",
                     8:"095c683c-ff7e-55f0-8266-8ba2d0320ed4",
                     9:"67ce294e-c10c-5024-b8ea-d0288bcd8d69"}

def make_unix_timestamp(date_string, time_string):
    """Returns the unix time stamp of a given date, date_string (format
    YYYY,MM,DD), and a given time, time_string (format HH,MM,SS)."""
    date_string_split = date_string.split(",")
    current_date = date(int(date_string_split[0]),
                        int(date_string_split[1]),
                        int(date_string_split[2]))
    current_unix = mktime(current_date.timetuple())
    time_string_split = time_string.split(",")
    current_time = 1000*(3600*int(time_string_split[0]) +
                    60*int(time_string_split[1]) +
                    int(time_string_split[2]))
    return str(int(current_unix + current_time))

def parse(url):
    """Returns a list of the timestamps, readings, and unixtimes of each
    entry from the raw data provided by the input url."""
    timestamp=[]
    reading=[]
    timest=[]
    temp=[]
    unixtime=[]
    webpage = urllib2.urlopen(url).read()
    page = str.split(webpage, '[')
    for count in range(len(page)):
        z1=str.split(page[count],',')
        temp.append(z1)
        count+=1
    getvar = temp[3:]
    for count in range(len(getvar)):
        t=float(getvar[count][0])/1000
        unixtime.append(float(getvar[count][0]))
        ttb=time.localtime(t)
        #Returns time in string format: "Wed 21 11 2012 16 45 53"
        tim=strftime("%a %d %m %Y %H %M %S",ttb)
        #For debugging:
        if (count == 0):
            print(tim)
        timestamp.append(tim.split())
        read=str.split((getvar[count][1]),']')
        reading.append(float(read[0]))
        #For debugging:
        if (count == 0):
            print(float(read[0])) #37.851485925
        count+=1
    return [timestamp, reading, unixtime]

def getSunpos(lat, lon, timezon, year, month, day, hour, minute, seconds):
    """Returns a list containing the altitude and the azimuth given the
    latitude LAT, longitude LON, timezone TIMEZON, year YEAR, month MONTH,
    minute MINUTE, and seconds SECONDS."""
    splat = str.split(lat)
    splon = str.split(lon)
    latitude = float(splat[0]) + float(splat[1])/60 + float(splat[2])/3600
    if splon[3] == 'W':
        longitude = -(float(splon[0]) + float(splon[1])/60 +
                      float(splon[2])/3600)
    else:
        longitude = float(splon[0]) + float(splon[1])/60 +\
        float(splon[2])/3600
    local = pytz.timezone(timezon)
    loctime = str(year) + '-' + str(month) + '-' + str(day) + ' ' +\
                str(hour) + ':' + str(minute) + ':' + str(seconds)
    naive = datetime.strptime(loctime, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    utc_dt.strftime("%Y-%m-%d %H:%M:%S")
    utcsplit = str.split(str(utc_dt))
    utcdt = str.split(utcsplit[0],'-')
    utctime = str.split(utcsplit[1],'+')
    utctimefinal = str.split(utctime[0],':')
    year = utcdt[0]
    month = utcdt[1]
    day = utcdt[2]
    hour = utctimefinal[0]
    minute = utctimefinal[1]
    second = utctimefinal[2]
    #+1 for e and -1 for w for dst
    houronly = float(hour) + float(minute)/60 + float(second)/3600
    delta = int(year)-1949
    leap = int(delta/4)
    doy = [31,28,31,30,31,30,31,31,30,31,30,31]
    if int(year)%4 == 0:
        doy[1] = 29
    dayofyear = sum(doy[0:(int(month)-1)]) + int(day)
    jd = 2432916.5 + delta*365 + dayofyear + leap + houronly/24
    actime = jd - 2451545
    pi = 3.1415926535897931
    rad = pi/180
    
    #mean longitude in degrees between 0 and 360
    L = (280.46 + 0.9856474*actime)%360
    if L < 0:
        L+=360
    #mean anomaly in radians
    g = (357.528 + 0.9856003*actime) % 360
    if g < 0:
        g+=360
    g = g*rad
    #ecliptic longitude in radians
    eclong = (L + 1.915*math.sin(g) + 0.02*math.sin(2*g)) % 360
    if eclong < 0:
        eclong+=360
    eclong = eclong*rad
    #ecliptic obliquity in radians
    ep = (23.439 - 0.0000004*actime)*rad
    #get right ascension in radians between 0 and 2 pi
    num = math.cos(ep)*math.sin(eclong)
    den = math.cos(eclong)
    ra = math.atan(num/den)
    if den < 0:
        ra+=pi
    elif den > 0 and num < 0:
        ra+=2*pi
    #get declination in radians
    dec = math.asin(math.sin(ep)*math.sin(eclong))
    #get greenwich mean sidereal time
    gmst = (6.697375 + 0.0657098242*actime + houronly) % 24
    if gmst < 0:
        gmst+=24
    #get local mean sidereal time in radians
    lmst=(gmst + longitude/15) % 24
    if lmst < 0:
        lmst+=24
    lmst = lmst*15*rad
    #get hour angle in radians between -pi and pi
    ha = lmst - ra
    if ha < -pi:
        ha+=2*pi
    elif ha > pi:
        ha = ha - 2*pi
    #change latitude to radians
    latrad = latitude*rad
    #calculate elevation and azimuth in degrees
    el=math.asin(math.sin(dec)*math.sin(latrad) +
                 math.cos(dec)*math.cos(latrad)*math.cos(ha))
    az=math.asin(-math.cos(dec)*math.sin(ha)/math.cos(el*rad))
    #approximation for azimuth
    #if az==90, elcrit=math.degrees(math.asin(math.sin(dec)/math.sin(latitude)))
    if math.sin(dec) - math.sin(el)/math.sin(latrad) >= 0 and\
        math.sin(az) < 0:
        az+=2*pi
    elif math.sin(dec) - math.sin(el)/math.sin(latrad) < 0:
        az = pi-az
    eldeg = round(math.degrees(el),2)
    azdeg = round(math.degrees(az),2)
    if eldeg > -0.56:
        refrac = 3.51561*(0.1594 + 0.0196*eldeg + 0.00002*math.pow(eldeg,2))\
                    /(1 + 0.505*eldeg + 0.0845*math.pow(eldeg,2))
    else:
        refrac = 0.56
    eldeg=eldeg+refrac
    #print eldeg,azdeg
    #data is saved for future reference
    return [str(eldeg), str(azdeg)]

def fill_gaps(timestamp, reading, unixtime):
    newunixtime = [round(x/300000.0)*300000.0 for x in unixtime]
    #eliminate duplicates
    i = 0
    size = len(newunixtime)
    while i < size-1:
        prev = newunixtime[i]
        curr = newunixtime[i+1]
        if (prev == curr):
            del newunixtime[i]
            del reading[i]
            del timestamp[i]
            size = size - 1
        i = i + 1
    #fill in the gaps
    n = unixtime[0]/300000
    counter = 0
    while (newunixtime[counter] < newunixtime[-1]):
        if newunixtime[counter] + 300000 < newunixtime[counter+1]:
            newunixtime.insert(counter + 1, (n+1)*300000)
            t = float((n+1)*300)
            ttb = time.localtime(t)
            tim = strftime("%a %d %m %Y %H %M %S", ttb)
            timestamp.insert(counter + 1, tim.split())
            reading.insert(counter + 1, float('nan'))
        n = n + 1
        counter = counter + 1
    return timestamp, reading, newunixtime

def createData(sens_no, nasa, start, end, lat, lon, timezon):
    """This function adds data for BEST lab sensor SENS_NO into its
    respective light table starting from unix timestamp (in milliseconds)
    START and ending at unix timestamp (in milliseconds) END. It generates
    sunposition data using the given LAT, LON, and TIMEZON. If these are
    not specified, createData resorts to the default LAT, LON, and TIMEZON
    values, which are the values for the BEST Lab in Berkeley, CA. LAT
    format is "degrees minutes seconds" (north is positive). LON format is
    "degrees minutes seconds W|E" (W for west and E for east). TIMEZON
    choices can be looked up. Must be compatible with python utc timezones.
    """
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    if nasa:
        sensorID = nasa_sensors_dict[sens_no]
        sensorLoc = nasa_sensors_loc[sens_no]
        table = "nasalight" + str(sens_no)
    else:
        sensorID = sensors_dict[sens_no]
        sensorLoc = sensors_loc[sens_no]
        table = "light" + str(sens_no)
    x = sensorLoc[0]
    y = sensorLoc[1]
    url = "http://new.openbms.org/backend/api/prev/uuid/" + sensorID +\
          "?&start=" + start + "&end=" + end + "&limit=100000&"
    timestamp, reading, unixtime = parse(url)
    # fill in the gaps in the unixtimes
    #timestamp, reading, unixtime = fill_gaps(timestamp, reading, unixtime)
    for count in range(len(reading)):
        time = timestamp[count]
        #print(time)
        sunpos = getSunpos(lat, lon, timezon, time[3], time[2],
                           time[1], time[4], time[5], time[6])
        cloud = cursor.execute('SELECT cloudiness FROM cloud WHERE day = ' +
                               str(time[1]) + ' AND month = ' + str(time[2]) +
                               ' AND year = ' + str(time[3]) + ' AND hour = ' +
                               str(time[4]))
        cloudiness = cloud.fetchone()
        if nasa == False:
            if cloudiness is not None:
                to_db = [unixtime[count], time[0], time[1], time[2], time[3],
                         time[4], time[5],time[6], reading[count], sunpos[0],
                         sunpos[1], str(cloudiness[0]), x, y, float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN'),
                         float('NaN'),float('Nan'),float('Nan')]
            else:
                to_db = [unixtime[count], time[0], time[1], time[2], time[3],
                         time[4], time[5],time[6], reading[count], sunpos[0],
                         sunpos[1], "None", x, y, float('NaN'), float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN'),
                         float('Nan'),float('Nan')]
            cursor.execute('INSERT OR IGNORE INTO ' + table +
                           ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           to_db)
        else:
            if cloudiness is not None:
                to_db = [unixtime[count], time[0], time[1], time[2], time[3],
                         time[4], time[5],time[6], reading[count], sunpos[0],
                         sunpos[1], str(cloudiness[0]), x, y, float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN'),
                         float('NaN')]
            else:
                to_db = [unixtime[count], time[0], time[1], time[2], time[3],
                         time[4], time[5],time[6], reading[count], sunpos[0],
                         sunpos[1], "None", x, y, float('NaN'), float('NaN'),
                         float('NaN'), float('NaN'), float('NaN'), float('NaN')]
            cursor.execute('INSERT OR IGNORE INTO ' + table +
                           ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           to_db)
    connection.commit()

    
def smoothinglight1exp():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    x = smoothing(1, False, 'exponential')
    for elem in x:
        cursor.execute('UPDATE light1 SET exponential = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()

def smoothinglight1avg():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    y = smoothing (1, False, 'average')
    for elem in y:
        cursor.execute('UPDATE light1 SET average = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()


def smoothinglight2exp():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    x = smoothing(2, False, 'exponential')
    for elem in x:
        cursor.execute('UPDATE light2 SET exponential = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()

    
def smoothinglight3exp():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    x = smoothing(3, False, 'exponential')
    for elem in x:
        cursor.execute('UPDATE light3 SET exponential = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()

    
def smoothinglight4exp():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    x = smoothing(4, False, 'exponential')
    for elem in x:
        cursor.execute('UPDATE light4 SET exponential = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()

def smoothinglight2avg():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    y = smoothing (2, False, 'average')
    for elem in y:
        cursor.execute('UPDATE light2 SET average = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()

def smoothinglight3avg():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    y = smoothing (3, False, 'average')
    for elem in y:
        cursor.execute('UPDATE light3 SET average = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()

def smoothinglight4avg():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    y = smoothing (1, False, 'average')
    for elem in y:
        cursor.execute('UPDATE light4 SET average = ' + str(elem[0]) + ' WHERE unixtime = ' + str(elem[1]))
    connection.commit()


def createLightData():
    createAllData()
    smoothinglight1exp()
    smoothinglight1avg()
    smoothinglight2exp()
    smoothinglight2avg()
    smoothinglight3exp()
    smoothinglight3avg()
    smoothinglight4exp()
    smoothinglight4avg()


def creatingAllData():
    """Adds all the data starting from the beginning of data collection
    until the current time for BEST lab sensors 2, 3, and 4 and Nasa ."""
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    createData(1, False, "1347059530000", str(int(time.time())*1000),
               best_lat, best_lon, best_timezone)
    createData(2, False, "1349478489000", str(int(time.time())*1000),
               best_lat, best_lon, best_timezone)
    createData(3, False, "1353545153000", str(int(time.time())*1000),
               best_lat, best_lon, best_timezone)
    createData(4, False, "1353545237000", str(int(time.time())*1000),
               best_lat, best_lon, best_timezone)
    createData(1, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(2, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(3, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(4, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(5, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(6, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(7, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(8, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    createData(9, True, "1335859200000", str(int(time.time())*1000), nasa_lat,
               nasa_lon, nasa_timezone)
    #Save your changes
    connection.commit()

def updateAllData():
    """Updates all the data in BEST lab sensors 2, 3, and 4 by calling
    updateData on each sensor."""
    updateData(1, False, best_lat, best_lon, best_timezone)
    updateData(2, False, best_lat, best_lon, best_timezone)
    updateData(3, False, best_lat, best_lon, best_timezone)
    updateData(4, False, best_lat, best_lon, best_timezone)
    updateData(1, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(2, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(3, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(4, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(5, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(6, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(7, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(8, True, nasa_lat, nasa_lon, nasa_timezone)
    updateData(9, True, nasa_lat, nasa_lon, nasa_timezone)

def updateData(sens_no, nasa, lat, lon, timezon):
    """Updates all the data starting from the time of the latest entry of
    each time table until the current time for BEST lab sensor number
    SENS_NO. It generates sunposition data using the given LAT, LON, and
    TIMEZON. If these are not specified, createData resorts to the default
    LAT, LON, and TIMEZON values, which are the values for the BEST Lab
    in Berkeley, CA. LAT format is "degrees minutes seconds" (north is
    positive). LON format is "degrees minutes seconds W|E" (W for west and
    E for east). TIMEZON choices can be looked up. Must be compatible with
    python utc timezones.
    """
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    if nasa:
        sensorID = nasa_sensors_dict[sens_no]
        sensorLoc = nasa_sensors_loc[sens_no]
        table = "nasalight" + str(sens_no)
    else:
        sensorID = sensors_dict[sens_no]
        sensorLoc = sensors_loc[sens_no]
        table = "light" + str(sens_no)
    x = sensorLoc[0]
    y = sensorLoc[1]
    cursor.execute('SELECT MAX(unixtime) FROM ' + table)
    start = int(cursor.fetchone()[0])
    end = int(time.time())*1000
    limit = (end - start)/300000
    print("limit is:" + str(limit))
    print("Start is:" + str(start))
    print("End is:" + str(end))
    createData(sens_no, start, end)
    #Save your changes
    connection.commit()




### TimeSeries(2) Code

#1st derivative, second derivative, moving mean, moving standard deviation, exponential smoothing



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
    nROC1=[]
    nRROC1=[]

    sensornumber = moteNum
    #get data
    if nasa:
        sensor='nasalight'+str(sensornumber)
    else:
        sensor='light'+str(sensornumber)
        
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    cursor.execute('SELECT light, unixtime, hour from %s' %(sensor))
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
    for count in range(len(data1)):
        if time1[count]-time1[count-1]<=6*300000 and data1[count]=='nan':
            if data1[count-1]!='nan':
                data1[count]=data1[count-1]
            else:
                data1[count]=1
            #data1[count]=np.mean(data1[count-2:count-1])
        elif time1[count]-time1[count-1]>6*300000 and data1[count]=='nan':
            data1[count]=1
            
    #rate of change
    for t in range(len(data1)-1):
        rate=data1[t+1]-data1[t]
        ROC1.append(rate)
        
    #rate of rate of change
    for n in range(len(ROC1)-1):
        changeofrate=ROC1[n+1]-ROC1[n]
        RROC1.append(changeofrate)
        
    #moving mean and standard deviation
    w= movingStatsWindow
    count=0
    while count<=w-1:
        average=np.mean(data1[count:w])
        std=np.std(data1[count:w])
        mean1.append((average, time1[count]))
        stdev1.append(std)
        count+=1
    count=w
    while count<=(len(data1)-w):
        average=np.mean(data1[count-w:count+w])
        std=np.std(data1[count-w:count+w])
        mean1.append((average, time1[count]))
        stdev1.append(std)
        count+=1
    while count>=len(data1)-w+1 and count<len(data1):
        average=np.mean(data1[count:len(data1)])
        std=np.std(data1[count:len(data1)])
        mean1.append((average,time1[count]))
        stdev1.append(std)
        count+=1
    for count in range(len(data1)):
        if data1[count]=='nan' or mean1[count]=='nan':
            print("WHAT THE HECK")

    p=expWindow
    alpha=Alpha

    for count in range(len(data1)):
        addsum1=0
        for add in range(p-1):
            term=float(alpha)*math.pow((1-float(alpha)),add)*data1[count-add]
            addsum1+=term
        smoothed=addsum1+math.pow((1-float(alpha)),p)*data1[count-p]
        esmooth1.append((smoothed,time1[count]))


    final=[time1,data1,mean1,esmooth1,stdev1]
    if smoothtype=='exponential':
        output=final[3]
    elif smoothtype=='average':
        output=final[2]

    return output



        
    

    

